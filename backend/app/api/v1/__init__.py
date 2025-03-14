from flask import Blueprint

# Import all API routes
from .auth import auth_bp
from .users import users_bp
from .notes import notes_bp
from .daily_messages import daily_messages_bp
from .bible_verses import bible_verses_bp


def register_routes(app):
    """Register all API routes with the Flask app"""
    # Create main API v1 blueprint
    api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

    # Register all route blueprints
    api_v1.register_blueprint(auth_bp)
    api_v1.register_blueprint(users_bp)
    api_v1.register_blueprint(notes_bp)
    api_v1.register_blueprint(daily_messages_bp)
    api_v1.register_blueprint(bible_verses_bp)

    # Register the main blueprint with the app
    app.register_blueprint(api_v1)
