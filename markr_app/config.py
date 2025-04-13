import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key')
    FLASK_APP = os.environ.get('FLASK_APP', 'markr_app.app')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Server
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))

class DevelopmentConfig(Config):
    """Development configuration"""
    FLASK_ENV = 'development'
    FLASK_DEBUG = True

class TestingConfig(Config):
    """Testing configuration"""
    FLASK_ENV = 'testing'
    FLASK_DEBUG = True
    
    # Always use test database for testing
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', '123456')
    DB_HOST = os.environ.get('DB_HOST', 'db')  # 'db' in Docker, 'localhost' otherwise
    DB_PORT = os.environ.get('DB_PORT', '5432')
    TEST_DATABASE_NAME = os.environ.get('TEST_DATABASE_NAME', 'markrdb_test')
    
    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DATABASE_NAME}"

class ProductionConfig(Config):
    """Production configuration"""
    FLASK_ENV = 'production'
    FLASK_DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}