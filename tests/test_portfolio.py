from decimal import Decimal
from datetime import date
from models.asset import Asset
from models.operation import Operation
from models.portfolio import Portfolio

def test_single_buy_operation():
    """
    Tests if a single 'Buy' operation is correctly registered in the portfolio.
    """
    # 1. ARRANGE: Set up the necessary objects for the test
    test_asset = Asset(ticker="TEST4", name="Test Asset Inc.", asset_type="Ação")
    
    test_operation = Operation(
        asset=test_asset,
        operation_date=date(2025, 1, 1),
        operation_type="Buy",
        quantity=Decimal("100"),
        unit_price=Decimal("10.00"),
        costs=Decimal("5.00")
    )
    
    portfolio = Portfolio()

    # 2. ACT: Perform the action we want to test
    portfolio.register_operation(test_operation)

    # 3. ASSERT: Check if the results are what we expect
    assert len(portfolio._positions) == 1
    
    position = portfolio.get_position("TEST4")
    assert position is not None
    assert position.quantity == 100
    
    # Check if the average price calculation is correct: ((100 * 10.00) + 5.00) / 100 = 10.05
    assert position.average_price == Decimal("10.05")
    assert position.total_cost == Decimal("1005.00")

def test_buy_and_sell_operation():
    """
    Tests a sequence of a Buy and a partial Sell operation.
    """
    # 1. ARRANGE
    test_asset = Asset(ticker="TEST4", name="Test Asset Inc.", asset_type="Ação")

    buy_op = Operation(
        asset=test_asset,
        operation_date=date(2025, 1, 1),
        operation_type="Buy",
        quantity=Decimal("100"),
        unit_price=Decimal("10.00"),
        costs=Decimal("5.00")
    )

    sell_op = Operation(
        asset=test_asset,
        operation_date=date(2025, 1, 5),
        operation_type="Sell",
        quantity=Decimal("40"), # Selling 40 of the 100 shares
        unit_price=Decimal("12.00"), # Selling at a higher price
        costs=Decimal("2.00") # Costs on the sale
    )

    portfolio = Portfolio()

    # 2. ACT
    portfolio.register_operation(buy_op)
    portfolio.register_operation(sell_op)

    # 3. ASSERT
    assert len(portfolio._positions) == 1

    position = portfolio.get_position("TEST4")
    assert position is not None

    # Assert the final quantity is correct (100 - 40 = 60)
    assert position.quantity == 60

    # Assert the average price DID NOT change after the sale
    # It should still be based on the original buy: ((100 * 10.00) + 5.00) / 100 = 10.05
    assert position.average_price == Decimal("10.05")

    # Assert the total cost basis is updated for the remaining shares
    # 60 shares * 10.05 avg_price = 603.00
    assert position.total_cost == Decimal("603.00")

def test_multiple_buy_operations():
    """
    Tests that multiple 'Buy' operations for the same asset correctly
    update the quantity and average price.
    """
    # 1. ARRANGE
    test_asset = Asset(ticker="TEST4", name="Test Asset Inc.", asset_type="Ação")

    # First buy: 100 shares @ R$10.00. Total cost = (100*10)+5 = 1005.00
    buy_op1 = Operation(
        asset=test_asset,
        operation_date=date(2025, 1, 1),
        operation_type="Buy",
        quantity=Decimal("100"),
        unit_price=Decimal("10.00"),
        costs=Decimal("5.00")
    )

    # Second buy: 50 more shares @ R$12.00. Total cost = (50*12)+2.50 = 602.50
    buy_op2 = Operation(
        asset=test_asset,
        operation_date=date(2025, 2, 1),
        operation_type="Buy",
        quantity=Decimal("50"),
        unit_price=Decimal("12.00"),
        costs=Decimal("2.50")
    )

    portfolio = Portfolio()

    # 2. ACT
    portfolio.register_operation(buy_op1)
    portfolio.register_operation(buy_op2)

    # 3. ASSERT
    assert len(portfolio._positions) == 1
    position = portfolio.get_position("TEST4")
    assert position is not None

    # Assert final quantity: 100 + 50 = 150
    assert position.quantity == 150

    # Assert final average price:
    # Total Cost = 1005.00 + 602.50 = 1607.50
    # Average Price = 1607.50 / 150 = 10.716666...
    expected_avg_price = Decimal("1607.50") / Decimal("150")
    assert position.average_price == expected_avg_price

    # Assert final total cost: 150 shares * 10.71666...
    assert position.total_cost == Decimal("1607.50")