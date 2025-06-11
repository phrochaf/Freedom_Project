from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional #para type hints

from .asset import Asset
from .operation import Operation
from .earning import Earning

class AssetPosition:
    def __init__(self, asset: Asset, quantity: Decimal = Decimal('0'), average_price: Decimal = Decimal('0')):
        self.asset = asset
        self.quantity = quantity
        self.average_price = average_price #preço médio de compra, incluindo custos
        self.total_cost = quantity * average_price

    def __str__(self):
        return (f"AssetPosition(Asset: {self.asset.ticker}, Qtd: {self.quantity:.2f}, "
                f"PM: R$ {self.average_price:.2f}, "
                f"Total Investido: R$ {self.total_cost:.2f})")
    
    def __repr__(self):
        return (f"AssetPosition(asset={repr(self.asset)}, "
                f"quantity=Decimal('{self.quantity}'), "
                f"average_price=Decimal('{self.average_price}'))")
    
class Portfolio:
    def __init__(self):
        self._positions: Dict[str, AssetPosition] = {} #dicionário de posições, chave é o ticker do ativo
        self._registered_operations: List[Operation] = []
        self._registered_earnings: List[Earning] = []

    def register_operation(self, operation: Operation):
        if not isinstance(operation, Operation):
            raise ValueError("operation must be an instance of Operation")
        
        self._registered_operations.append(operation)
        ticker = operation.asset.ticker

        if ticker not in self._positions:
            self._positions[ticker] = AssetPosition(operation.asset)

        current_position = self._positions[ticker]
        operation_effective_value = operation.effective_value()

        if operation.operation_type == 'Buy':
            #Calcula o novo preço médio
            previous_total_cost = current_position.quantity * current_position.average_price
            new_quantity = current_position.quantity + operation.quantity

            if new_quantity > 0:
                new_total_cost = previous_total_cost + operation_effective_value
                current_position.average_price = new_total_cost / new_quantity
            else:
                #Se a quantidade for negativa, a posição é zerada
                current_position.average_price = Decimal('0')

            current_position.quantity = new_quantity
        
        elif operation.operation_type == 'Sell':
            current_position.quantity -= operation.quantity

            if current_position.quantity < Decimal('0'):
                print(f"Warning: Sale of {operation.quantity} {ticker} resulted in negative quantity. Setting to 0.")
                current_position.quantity = Decimal('0')

            if current_position.quantity == Decimal('0'):
                current_position.average_price = Decimal('0')

        current_position.total_cost = current_position.quantity * current_position.average_price
    
    def register_earning(self, earning: Earning):
        if not isinstance(earning, Earning):
            raise ValueError("earning must be an instance of Earning")
        
        self._registered_earnings.append(earning)
        print(f"Earning of {earning.asset.ticker} registered on {earning.pay_date.strftime('%d/%m/%Y')}")

    def get_position(self, ticker: str) -> Optional[AssetPosition]:
        return self._positions.get(ticker)
    
    @property
    def total_cost(self):
        return sum(pos.total_cost for pos in self._positions.values())
    
    def __str__(self):
        num_positions = len([p for p in self._positions.values() if p.quantity > Decimal('0')])
        return (f"Portfolio with {num_positions} active positions and {len(self._registered_operations)} operations registered")
    
    def __repr__(self):
            return (f"Portfolio(positions={len(self._positions)}, operations={len(self._registered_operations)}, earnings={len(self._registered_earnings)})")
        

