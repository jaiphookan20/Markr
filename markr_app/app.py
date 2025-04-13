import os
from flask import Flask
from markr_app.config import config
from markr_app.database import db
from markr_app.utils.errors import register_error_handlers
from markr_app.views.api import api_bp

def create_app(config_name=None):
    """Create & configure the Flask app"""
    app = Flask(__name__)

    # Determine the config to use
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    # Load config
    app.config.from_object(config[config_name])
    db.init_app(app)

    # Register API blueprint
    app.register_blueprint(api_bp)

    # Register the error handlers
    register_error_handlers(app)

    # Create the DB tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])


        