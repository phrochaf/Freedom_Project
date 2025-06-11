from datetime import date
from decimal import Decimal
from database import db
from .asset import Asset

class Earning(db.Model):
    __tablename__ = 'earning'

    id = db.Column(db.Integer, primary_key=True)
    pay_date = db.Column(db.Date, nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    net_value_per_unit = db.Column(db.Numeric(18, 2), nullable=False)
    earning_type = db.Column(db.String(50), nullable=False)

    asset = db.relationship('Asset', backref=db.backref('earnings', lazy=True))

    def __str__(self):
        ticker = self.asset.ticker if self.asset else "N/A"
        return (f"Earning {self.id}, ({self.earning_type} of {ticker}"
                f"- R$ {self.net_value_per_unit:.2f}/unidade"
                f"em {self.pay_date.strftime('%d/%m/%Y')})")
    
    def __repr__(self):
        ticker = self.asset.ticker if self.asset else "N/A"
        return (f"Earning {self.id} (pay_date={self.pay_date.year}, {self.pay_date.month}, {self.pay_date.day}, "
                f"asset={repr(ticker)}, "
                f"net_value_per_unit=Decimal('{self.net_value_per_unit}'), "
                f"earning_type='{self.earning_type}')")
    



