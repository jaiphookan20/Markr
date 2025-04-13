import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key')
    FLASK_APP = os.environ.get('FLASK_APP', 'markr_app.app')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Server
    HOST = os.environ.get('HOST', '0.0.0.0');
    PORT = os.environ.get('PORT', 5000);

class DevelopmentConfig(Config):
    """Development configuration"""
    FLASK_ENV = 'development'
    FLASK_DEBUG = True

class TestingConfig(Config):
    """Testing configuration"""
    FLASK_ENV = 'testing'
    FLASK_DEBUG = True

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}