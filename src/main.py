from datetime import date
from decimal import Decimal

# Importando nossas classes do pacote 'models' USANDO IMPORTAÇÃO RELATIVA
from .models.asset import Ativo
from .models.operation import Operacao
from .models.earning import Provento
from .models.portfolio import Carteira, PosicaoAtivo

def main():
    print("Iniciando simulação do Gestor de Investimentos...")

    # 1. Criar alguns ativos
    ativo1 = Ativo(ticker="PETR4", nome_empresa_ou_fundo="Petróleo Brasileiro S.A.", tipo_ativo="Ação")
    ativo2 = Ativo(ticker="MXRF11", nome_empresa_ou_fundo="Maxi Renda FII", tipo_ativo="FII")
    ativo3 = Ativo(ticker="VALE3", nome_empresa_ou_fundo="Vale S.A.", tipo_ativo="Ação")

    print(f"\nAtivo criado: {ativo1}")
    print(f"Ativo criado: {repr(ativo2)}")

    # 2. Criar uma carteira
    minha_carteira = Carteira()
    print(f"\nCarteira criada: {minha_carteira}")

    # 3. Registrar operações
    print("\n--- Registrando Operações ---")
    op1 = Operacao(
        data_operacao=date(2024, 1, 15),
        ativo_objeto=ativo1, # PETR4
        quantidade=Decimal('100'),
        preco_unitario=Decimal('30.00'),
        tipo_operacao='Compra',
        custos_operacionais=Decimal('5.50')
    )
    minha_carteira.registrar_operacao(op1)
    print(f"Operação registrada: {op1}")

    op2 = Operacao(
        data_operacao=date(2024, 2, 10),
        ativo_objeto=ativo2, # MXRF11
        quantidade=Decimal('50'),
        preco_unitario=Decimal('10.50'),
        tipo_operacao='Compra',
        custos_operacionais=Decimal('2.75')
    )
    minha_carteira.registrar_operacao(op2)
    print(f"Operação registrada: {op2}")

    op3 = Operacao(
        data_operacao=date(2024, 3, 5),
        ativo_objeto=ativo1, # PETR4
        quantidade=Decimal('50'),
        preco_unitario=Decimal('32.00'),
        tipo_operacao='Compra',
        custos_operacionais=Decimal('3.00')
    )
    minha_carteira.registrar_operacao(op3)
    print(f"Operação registrada: {op3}")

    # 4. Exibir resumo da carteira após as compras
    minha_carteira.resumo_carteira()

    # 5. Registrar uma operação de venda
    print("\n--- Registrando Venda ---")
    op4 = Operacao(
        data_operacao=date(2024, 4, 1),
        ativo_objeto=ativo1, # PETR4
        quantidade=Decimal('30'),
        tipo_operacao='Venda',
        preco_unitario=Decimal('35.00'),
        custos_operacionais=Decimal('2.00')
    )
    minha_carteira.registrar_operacao(op4)
    print(f"Operação registrada: {op4}")

    # 6. Exibir resumo da carteira após a venda
    minha_carteira.resumo_carteira()

    # 7. Registrar um provento
    print("\n--- Registrando Provento ---")
    prov1 = Provento(
        data_pagamento=date(2024, 5, 15),
        ativo_objeto=ativo2, # MXRF11
        valor_liquido_por_unidade=Decimal('0.10'), # CORRIGIDO AQUI
        tipo_provento='Rendimento FII'
    )
    minha_carteira.registrar_provento(prov1)
    print(f"Total de proventos recebidos: {len(minha_carteira._proventos_recebidos)}")

    # 8. Testar compra de ativo já existente após zerar posição
    print("\n--- Testando Venda Total e Recompra ---")
    op_venda_total_mxrf11 = Operacao(
        data_operacao=date(2024, 6, 1),
        ativo_objeto=ativo2, # MXRF11
        quantidade=Decimal('50'),
        tipo_operacao='Venda',
        preco_unitario=Decimal('11.00'),
        custos_operacionais=Decimal('2.75')
    )
    minha_carteira.registrar_operacao(op_venda_total_mxrf11)
    print(f"Operação registrada: {op_venda_total_mxrf11}")
    minha_carteira.resumo_carteira()

    op_recompra_mxrf11 = Operacao(
        data_operacao=date(2024, 6, 15),
        ativo_objeto=ativo2, # MXRF11
        quantidade=Decimal('20'),
        preco_unitario=Decimal('10.80'),
        tipo_operacao='Compra',
        custos_operacionais=Decimal('1.50')
    )
    minha_carteira.registrar_operacao(op_recompra_mxrf11)
    print(f"Operação registrada: {op_recompra_mxrf11}")
    minha_carteira.resumo_carteira()

if __name__ == "__main__":
    main()