from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'testing':
        app.config.from_object('app.config.config.TestingConfig')
    else:
        app.config.from_object('app.config.config.Config')
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    
    # Setup CORS
    CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGIN", "*")}})
    
    # Register blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200
    
    return app