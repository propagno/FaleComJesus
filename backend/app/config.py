import os
from datetime import timedelta
from cryptography.fernet import Fernet


class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get(
        'SECRET_KEY', 'dev_secret_key_change_in_production')
    JWT_SECRET_KEY = os.environ.get(
        'JWT_SECRET_KEY', 'dev_jwt_secret_key_change_in_production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # RabbitMQ configuration
    RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://localhost:5672')

    # API Encryption (AES-256)
    API_ENCRYPTION_KEY = os.environ.get(
        'API_ENCRYPTION_KEY', Fernet.generate_key().decode())

    # Elastic Stack configuration
    ELASTICSEARCH_URL = os.environ.get(
        'ELASTICSEARCH_URL', 'http://localhost:9200')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'
    USE_MOCK_LLM = os.environ.get('USE_MOCK_LLM', 'False').lower() == 'true'
    LLM_SIMULATION_MODE = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/falecomjesus')


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/falecomjesus_test')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=10)


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # In production, we must use secure keys
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    API_ENCRYPTION_KEY = os.environ.get('API_ENCRYPTION_KEY')

    # Secure cookies
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    # CORS restrictions
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'https://falecomjesus.com')
