import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration — shared across all environments."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')

    # MySQL connection via PyMySQL
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.environ.get('DB_USERNAME')}:"
        f"{os.environ.get('DB_PASSWORD')}@"
        f"{os.environ.get('DB_HOST', 'localhost')}:"
        f"{os.environ.get('DB_PORT', '3306')}/"
        f"{os.environ.get('DB_NAME')}"
    )

    # Disable modification tracking — saves memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Development environment — debug on."""
    DEBUG = True


class ProductionConfig(Config):
    """Production environment — debug off."""
    DEBUG = False


# Map string names to config classes
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}