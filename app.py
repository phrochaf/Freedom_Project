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

from src.models.asset import Asset
from src.models.operation import Operation
from src.models.portfolio import Portfolio
from src.models.earning import Earning

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///investiments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    page_title = "Freedom Investment Manager"
    investor_tasks = [
        "Review the portfolio summary",
        "Analyze new assets for investment",
        "Register the latest buy/sell operations",
        "Study asset diversification"
    ]
    return render_template('index.html', 
                           title=page_title, 
                           task_list=investor_tasks)

@app.route('/portfolio')
def show_portfolio():

        # 1. Get operations from database
        db_operations = db.session.scalars(db.select(Operation).order_by(Operation.operation_date)).all()
        calculated_portfolio = Portfolio()
        for op in db_operations:
            calculated_portfolio.register_operation(op)
        
        #2. Fetch data from Yahoo Finance
        enriched_positions = []
        total_market_value = Decimal('0.00')

        #Get all tickers from database
        tickers_list = [pos.asset.ticker for pos in calculated_portfolio._positions.values() if pos.quantity > 0]

        if tickers_list:
            #Append ".SA" to tickers for Yahoo Finance
            tickers_yahoo_string = " ".join(f"{ticker}.SA" for ticker in tickers_list)
            tickers_data = yf.Tickers(tickers_yahoo_string)

        for position_obj in calculated_portfolio._positions.values():
            if position_obj.quantity <= 0:
                continue #skip if no quantity

            ticker_str = position_obj.asset.ticker
            ticker_data = tickers_data.tickers.get(f"{ticker_str}.SA")

            current_price = ticker_data.info.get('regularMarketPrice') if ticker_data and ticker_data.info else None 
            market_value = Decimal(str(current_price)) * position_obj.quantity if current_price else None
            profit_loss = market_value - position_obj.total_cost if market_value else None

            if market_value:
                total_market_value += market_value
            
            enriched_positions.append({
                 'position': position_obj,
                 'current_price': current_price,
                 'market_value': market_value,
                 'profit_loss': profit_loss
            })

        total_cost_basis = calculated_portfolio.total_cost
        total_profit_loss = total_market_value - total_cost_basis
        
        #3. Render template
        return render_template('portfolio.html',
                                positions=enriched_positions,
                                total_market_value=total_market_value, 
                                total_profit_loss=total_profit_loss, 
                                total_cost_basis=total_cost_basis)

@app.route('/add_operation', methods=['GET','POST'])
def add_operation():
    if request.method == 'POST':
        try:
            # 1. Get data from form
            ticker_str = request.form.get('ticker','').strip().upper()
            asset_name = request.form.get('asset_name','').strip()
            asset_type = request.form.get('asset_type')
            operation_type = request.form.get('operation_type')
            quantity = Decimal(request.form.get('quantity'))
            unit_price = Decimal(request.form.get('unit_price'))
            operation_date_str = request.form.get('operation_date')
            operation_date = datetime.strptime(operation_date_str, '%Y-%m-%d').date()
            costs = Decimal(request.form.get('costs', '0'))

            # 2. Database Logic
            asset_obj = db.session.scalar(db.select(Asset).filter_by(ticker=ticker_str))

            if asset_obj is None:
                if not asset_name or not asset_type:
                    print(f"ERROR: Ticker '{ticker_str}' is new, but name or type were not provided.")
                    return redirect(url_for('add_operation'))

                asset_obj = Asset(
                    ticker=ticker_str,
                    name=asset_name,
                    type=asset_type
                )
                db.session.add(asset_obj)
                db.session.commit()
                print(f"Asset '{ticker_str}' created successfully.")
            
            # 3. Create operation object
            new_operation = Operation(
                operation_date=operation_date,
                quantity=quantity,
                unit_price=unit_price,
                operation_type=operation_type,
                costs=costs,
                asset=asset_obj # Use the 'asset' relationship
            )
            # 4. Add new operation
            db.session.add(new_operation)
            db.session.commit()

            print(f"Operation saved to database: {new_operation}")

            return redirect(url_for('show_portfolio'))
        
        except (ValueError, InvalidOperation) as e:
            db.session.rollback()
            print(f"Error processing form: {e}")
            return redirect(url_for('add_operation'))
        except Exception as e:
            db.session.rollback()
            print(f"Unexpected error processing form: {e}")
            import traceback
            traceback.print_exc()
            return redirect(url_for('add_operation'))

    return render_template('add_operation.html')

@app.route('/analysis')
def analysis():
    # Get operations from database
    db_operations = db.session.scalars(db.select(Operation)).all()

    if not db_operations:
        return "<h3>No operations in the database to analyze.</h3><p><a href='/add_operation'>Add one!</a></p>"
    
    # Create the DataFrame
    data_for_df = [
        {
            'date': op.operation_date,
            'ticker': op.asset.ticker,
            'type': op.operation_type,
            'quantity': op.quantity,
            'unit_price': op.unit_price,
            'costs': op.costs,
        }
        for op in db_operations
    ]

    #3. Create pandas DataFrame
    df = pd.DataFrame(data_for_df)

    df['quantity'] = pd.to_numeric(df['quantity'])
    df['unit_price'] = pd.to_numeric(df['unit_price'])
    df['costs'] = pd.to_numeric(df['costs'])

    # Pandas Analysis
    #Filter for buys ops
    df_buys = df[df['type'] == 'Buy'].copy()

    #Total cost for op
    df_buys['total_cost'] = df_buys['quantity'] * df_buys['unit_price'] + df_buys['costs']

    #Group by ticker and sum costs
    invested_by_asset = df_buys.groupby('ticker')['total_cost'].sum()

    # Matplotlib Plot

    plt.figure(figsize=(10,6))
    invested_by_asset.plot(kind='bar', color='skyblue')
    plt.title('Total Invested by Asset')
    plt.xlabel('Asset')
    plt.ylabel('Total Invested (R$)')
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
    return render_template('analysis.html',
                            plot_url=img_path_relative,
                            data_html=invested_by_asset.to_frame().to_html(classes='data_table', float_format='{:,.2f}'.format))


if __name__ == '__main__':
    app.run(debug=True)

