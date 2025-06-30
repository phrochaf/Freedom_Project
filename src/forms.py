from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, DecimalField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from src.models.user import User
from src.database import db

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

def validate_username(self, username):
    user = db.session.scalar(db.select(User).where(User.username == username.data))
    if user is not None:
        raise ValidationError('Please use a different username.')
    
def validate_email(self, email):
    user = db.session.scalar(db.select(User).where(User.email == email.data))
    if user is not None:
        raise ValidationError('Please use a different email address.')
    
class OperationForm(FlaskForm):
    ticker = StringField('Ticker', validators=[DataRequired(), Length(min=3, max=10)])
    asset_name = StringField('Asset Name', validators=[Optional(), Length(min=3, max=100)])
    asset_type = SelectField('Asset Type', choices=[
        ('stock', 'Ação'),
        ('reit', 'FII'),
        ('fund', 'Fundo'),
        ('fixed_income', 'Renda Fixa'),
        ('bond', 'Título'),
        ('etf', 'ETF'),
        ('bdr', 'BDR'),
        ('crypto', 'Criptomoeda')
    ], validators=[Optional()])
    operation_type = SelectField('Operation Type', choices=[('buy', 'Compra'), ('sell', 'Venda')], validators=[Optional()])
    quantity = DecimalField('Quantity', validators=[Optional()])
    unit_price = DecimalField('Unit Price', validators=[Optional()])
    operation_date = DateField('Operation Date', validators=[Optional()])
    costs = DecimalField('Costs', validators=[Optional()])

    submit = SubmitField('Save Operation')
