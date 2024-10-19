import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Load configuration according to environment
    if os.environ.get("FLASK_ENV") == 'production':
        SECRET_KEY = os.environ.get('PROD_SECRET_KEY')
        SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_SQLALCHEMY_DATABASE_URI')
    elif os.environ.get("FLASK_ENV") == 'staging':
        SECRET_KEY = os.environ.get('STG_SECRET_KEY')
        SQLALCHEMY_DATABASE_URI = os.environ.get('STG_SQLALCHEMY_DATABASE_URI')
    elif os.environ.get("FLASK_ENV") == 'test':
        SECRET_KEY = os.environ.get('TEST_SECRET_KEY')
        SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_SQLALCHEMY_DATABASE_URI')
    else:
        SECRET_KEY = os.environ.get('DEV_SECRET_KEY')
        SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_SQLALCHEMY_DATABASE_URI')
    
    @staticmethod
    def init_app(app):
        pass