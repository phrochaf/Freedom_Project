from datetime import date
from decimal import Decimal
from database import db
from .asset import Asset

class Operation(db.Model):
    __tablename__ = 'operation'

    id = db.Column(db.Integer, primary_key=True)
    operation_date = db.Column(db.Date, nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    quantity = db.Column(db.Numeric(18, 8), nullable=False)
    unit_price = db.Column(db.Numeric(18, 2), nullable=False)
    operation_type = db.Column(db.String(10), nullable=False)
    costs = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))

    asset = db.relationship('Asset', backref=db.backref('operations', lazy=True))

    def gross_value(self) -> Decimal:
        return self.quantity * self.unit_price
    
    def effective_value(self) -> Decimal:

        total = self.gross_value()
        if self.operation_type == 'Buy':
            return total + self.costs
        elif self.operation_type == 'Sell':
            return total - self.costs
        return total 
    
    def __str__(self):
        ticker = self.asset.ticker if self.asset else "N/A" 
        return (f"Operation({self.operation_type} of {self.quantity} {ticker} "
               f"on {self.operation_date.strftime('%d/%m/%Y')}) at R$ {self.unit_price:.2f} "
               f"| Costs: R$ {self.costs:.2f})")
    
    def __repr__(self):
        ticker = self.asset.ticker if self.asset else "N/A"
        return (f"<Operation ID: {self.id}, Type: {self.operation_type}, Asset: {ticker}>")
    

