import pytest
from app import flask_app
from app import db as sqlalchemy_db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Configure the app for testing
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test_secret_key",
    })

    yield flask_app

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def db(app):
    """Create a database for the tests."""
    with app.app_context():
        sqlalchemy_db.create_all()
        yield sqlalchemy_db
        sqlalchemy_db.session.remove()
        sqlalchemy_db.drop_all()