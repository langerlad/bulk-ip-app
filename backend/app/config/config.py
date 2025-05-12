import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AbuseIPDB API settings
    ABUSEIPDB_API_KEY = os.getenv('ABUSEIPDB_API_KEY')
    ABUSEIPDB_API_URL = 'https://api.abuseipdb.com/api/v2'
    ABUSEIPDB_MAX_AGE_DAYS = 30
    
    # Export settings
    EXPORT_FOLDER = os.path.join(os.getcwd(), 'reports')
    CSV_FOLDER = os.path.join(EXPORT_FOLDER, 'csv')
    HTML_FOLDER = os.path.join(EXPORT_FOLDER, 'html')
    EXPORT_EXPIRY = timedelta(hours=24)  # Files older than this will be auto-deleted
    
    # Rate limiting
    RATELIMIT_DEFAULT = "50 per hour"
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    
    # IP Whitelist - set to None to disable
    IP_WHITELIST = os.getenv('IP_WHITELIST', None)
    
    # If True, creates required folders on startup
    INIT_EXPORT_FOLDERS = True
    
    # Flask API key
    FLASK_KEY = os.getenv('FLASK_KEY', 'dev-key')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENV = 'development'
    

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    ENV = 'testing'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    ENV = 'production'
    
    # Override with stronger settings for production
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Stricter rate limits for production
    RATELIMIT_DEFAULT = "100 per day"