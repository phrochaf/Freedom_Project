import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Set the backend for Matplotlib to work in a web server context
import matplotlib.pyplot as plt # The primary plotting interface
import os # To handle file paths

from flask import Flask, render_template, request, redirect, url_for
from database import db
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from src.models.asset import Ativo
from src.models.operation import Operacao
from src.models.portfolio import Carteira

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///investiments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)



@app.route('/')
def index():
    titulo_dinamico = "Página Inicial Dinâmica do Gestor"
    tarefas_investidor= [
        "Revisar o resumo da carteira",
        "Analisar novos FIIs para investir",
        "Registrar as últimas operações de compra/venda",
        "Estudar sobre diversificação de ativos"
    ]
    return render_template('index.html', titulo=titulo_dinamico, lista_de_tarefas=tarefas_investidor)

@app.route('/portfolio')
def show_portfolio():

        # 1. Get operations from database
        operacoes_db = db.session.scalars(db.select(Operacao).order_by(Operacao.data_operacao)).all()
        carteira_calculada = Carteira()
        for op in operacoes_db:
            carteira_calculada.registrar_operacao(op)
        
        #2. Fetch data from Yahoo Finance
        posicoes_enriquecidas = []
        total_market_value = Decimal('0.00')

        #Get all tickers from database
        tickers_list = [pos.ativo.ticker for pos in carteira_calculada._posicoes.values() if pos.quantidade > 0]

        if tickers_list:
            #Append ".SA" to tickers for Yahoo Finance
            tickers_yahoo_string = " ".join(f"{ticker}.SA" for ticker in tickers_list)

        tickers_data = yf.Tickers(tickers_yahoo_string)

        for posicao_obj in carteira_calculada._posicoes.values():
            if posicao_obj.quantidade <= 0:
                continue #skip if no quantity

            ticker_str = posicao_obj.ativo.ticker
            ticker_data = tickers_data.tickers.get(f"{ticker_str}.SA")

            current_price = None
            if ticker_data and ticker_data.info:
                current_price = ticker_data.info.get('regularMarketPrice')
            
            market_value = Decimal(str(current_price)) * posicao_obj.quantidade if current_price else None
            profit_loss = market_value - posicao_obj.valor_total_investido if market_value else None

            if market_value:
                total_market_value += market_value
            
            posicoes_enriquecidas.append({
                 'posicao': posicao_obj,
                 'current_price': current_price,
                 'market_value': market_value,
                 'profit_loss': profit_loss
            })

        total_cost_basis = carteira_calculada.valor_total_carteira
        total_profit_loss = total_market_value - total_cost_basis
        
        #3. Render template
        return render_template('portfolio.html', posicoes=posicoes_enriquecidas, total_market_value=total_market_value, total_profit_loss=total_profit_loss, total_cost_basis=total_cost_basis)

@app.route('/add_operation', methods=['GET','POST'])
def add_operation():
    if request.method == 'POST':
        try:
            # 1. Get data from form
            ticker_str = request.form.get('ticker','').strip().upper()
            nome_empresa = request.form.get('nome_empresa','').strip()
            tipo_ativo = request.form.get('tipo_ativo')
            
            # Other data
            tipo_operacao = request.form.get('tipo_operacao')
            quantidade = Decimal(request.form.get('quantidade'))
            preco_unitario = Decimal(request.form.get('preco_unitario'))
            data_operacao_str = request.form.get('data_operacao')
            data_operacao = datetime.strptime(data_operacao_str, '%Y-%m-%d').date()
            custos_operacionais = Decimal(request.form.get('custos_operacionais', '0'))

            # 2. Database Logic
            ativo_obj = db.session.scalar(db.select(Ativo).filter_by(ticker=ticker_str))

            if ativo_obj is None:
                if not nome_empresa or not tipo_ativo:
                    print(f"ERRO: Ticker '{ticker_str}' é novo, mas nome ou tipo não foram fornecidos.")
                    return redirect(url_for('add_operation'))

                ativo_obj = Ativo(
                    ticker=ticker_str,
                    nome_empresa_ou_fundo=nome_empresa,
                    tipo_ativo=tipo_ativo
                )
                db.session.add(ativo_obj)
                db.session.commit()
                print(f"Ativo '{ticker_str}' criado com sucesso.")
            
            # 3. Create operation object
            nova_operacao = Operacao(
                data_operacao=data_operacao,
                quantidade=quantidade,
                preco_unitario=preco_unitario,
                tipo_operacao=tipo_operacao,
                custos_operacionais=custos_operacionais,
                ativo_rel=ativo_obj
            )

            # 4. Add new operation
            db.session.add(nova_operacao)
            db.session.commit()

            print(f"Operação salva no banco de dados: {nova_operacao}")

            return redirect(url_for('show_portfolio'))
        
        except (ValueError, InvalidOperation) as e:
            db.session.rollback()
            print(f"Erro ao processar formulário: {e}")
            return redirect(url_for('add_operation'))
        except Exception as e:
            db.session.rollback()
            print(f"Erro inesperado ao processar formulário: {e}")
            import traceback
            traceback.print_exc()
            return redirect(url_for('add_operation'))

    return render_template('add_operation.html')

@app.route('/analysis')
def analysis():
    # Get operations from database
    operacoes_db = db.session.scalars(db.select(Operacao)).all()

    if not operacoes_db:
        return "<h3>No operations in the database to analyze.</h3><p><a href='/add_operation'>Add one!</a></p>"
    
    # Create the DataFrame
    data_for_df = [
        {
            'date': op.data_operacao,
            'ticker': op.ativo_rel.ticker,
            'type': op.tipo_operacao,
            'quantity': op.quantidade,
            'unit_price': op.preco_unitario,
            'costs': op.custos_operacionais,
        }
        for op in operacoes_db
    ]

    #3. Create pandas DataFrame
    df = pd.DataFrame(data_for_df)

    df['quantity'] = pd.to_numeric(df['quantity'])
    df['unit_price'] = pd.to_numeric(df['unit_price'])
    df['costs'] = pd.to_numeric(df['costs'])

    # Pandas Analysis
    #Filter for buys ops
    df_compras = df[df['type'] == 'Compra'].copy()

    #Total cost for op
    df_compras['total_cost'] = df_compras['quantity'] * df_compras['unit_price'] + df_compras['costs']

    #Group by ticker and sum costs
    investido_por_ativo = df_compras.groupby('ticker')['total_cost'].sum()

    # Matplotlib Plot

    # Create the Plot
    plt.figure(figsize=(10,6))
    investido_por_ativo.plot(kind='bar', color='skyblue')
    plt.title('Total Investido por Ativo')
    plt.xlabel('Ativo')
    plt.ylabel('Total Investido (R$)')
    plt.xticks(rotation=45)
    plt.tight_layout()

    #Save the plot to a file
    #We use a version number in the filename to help the browser avoid caching old images
    img_version = int(datetime.now().timestamp())
    img_path_relative = f'investments_by_asset_v{img_version}.png'
    img_path_full = os.path.join(app.root_path, 'static', img_path_relative)
    plt.savefig(img_path_full)
    plt.close()

    #Render the template with the plot
    return render_template('analysis.html', plot_url=img_path_relative, data_html=investido_por_ativo.to_frame().to_html(classes='data_table', float_format='{:,.2f}'.format))


if __name__ == '__main__':
    app.run(debug=True)

