import os
from app import create_app
from flask.cli import FlaskGroup

app = create_app()
cli = FlaskGroup(app)

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Set host to 0.0.0.0 to make it accessible from outside the container
    # in production, you should set up a reverse proxy with proper security
    host = os.environ.get('HOST', '0.0.0.0')
    
    # Debug mode should be disabled in production
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)