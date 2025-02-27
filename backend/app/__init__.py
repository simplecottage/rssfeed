from flask import Flask
from flask_cors import CORS
import os
from .database import init_db

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DATABASE=os.path.join(app.instance_path, 'news_aggregator.sqlite'),
    )

    # Enable CORS
    CORS(app)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize the database
    init_db(app)

    # Register routes
    from .routes import register_routes
    register_routes(app)

    return app
