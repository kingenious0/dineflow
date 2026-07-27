"""
Application Configuration for DineFlow Restaurant Management System.
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    """Base Configuration Class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dineflow-dev-key-2026')

    # Database
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'dineflow_db')

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f"mysql+pymysql://{os.getenv('MYSQL_USER','root')}:{os.getenv('MYSQL_PASSWORD','root')}@{os.getenv('MYSQL_HOST','localhost')}:{os.getenv('MYSQL_PORT',3306)}/{os.getenv('MYSQL_DATABASE','dineflow_db')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Business Defaults
    BUSINESS_NAME = os.getenv('BUSINESS_NAME', 'DineFlow Restaurant')
    CURRENCY = os.getenv('CURRENCY', 'GHS')
    TAX_RATE = float(os.getenv('TAX_RATE', 0.00))

    # Security & Session
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True

    # File Upload
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB


class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing Configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() in ('true', '1', 'yes')

    @classmethod
    def init_app(cls, app):
        secret = os.getenv('SECRET_KEY')
        if not secret or secret == 'dineflow-dev-key-2026':
            import warnings
            warnings.warn(
                "CRITICAL: Production environment is using default SECRET_KEY! Set a strong SECRET_KEY.",
                RuntimeWarning
            )


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
