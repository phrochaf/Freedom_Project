from database import db

class Asset(db.Model):
    __tablename__ = 'asset'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    asset_type = db.Column(db.String(20), nullable=False)
   
    def __repr__(self):
        return f"<Asset {self.ticker} (ID: {self.id})>"

    def __str__(self):
        return f"Asset(Ticker: {self.ticker}, Nome: {self.name}, Tipo: {self.asset_type})"
    
