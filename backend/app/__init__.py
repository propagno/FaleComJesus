import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token
import logging

from app.models.database import db
from app.api.auth import auth_bp
from app.api.notes import notes_bp
from app.api.api_keys import api_keys_bp
from app.api.chat import chat_bp
from app.api.conversations import conversations_bp
from app.api.prompt_templates import prompt_templates_bp
from app.utils.rate_limit import rate_limiter
from app.api.v1 import register_routes
from app.config import DevelopmentConfig, TestingConfig, ProductionConfig


def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__, instance_relative_config=True)

    # Configurar logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    # Configuração para não redirecionar URLs sem barra no final
    app.url_map.strict_slashes = False

    # Determine which configuration to use
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object(ProductionConfig)
    elif env == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Override config with test config if provided
    if test_config:
        app.config.update(test_config)

    # Initialize Flask extensions
    db.init_app(app)
    # Configurar CORS para permitir requisições do frontend em desenvolvimento
    CORS(app,
         resources={r"/*": {"origins": "http://localhost:3000"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization",
                        "X-Requested-With", "Accept", "Origin"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         expose_headers=["Content-Type", "Authorization"]
         )
    Migrate(app, db)
    JWTManager(app)

    # Setup Redis if configured
    if app.config.get('REDIS_URL'):
        import redis
        app.extensions['redis'] = redis.from_url(app.config['REDIS_URL'])
        rate_limiter.redis = app.extensions['redis']

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(api_keys_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(conversations_bp)
    app.register_blueprint(prompt_templates_bp)

    # Register API v1 routes
    register_routes(app)

    # Adiciona cabeçalhos CORS a todas as respostas
    @app.after_request
    def add_cors_headers(response):
        response.headers.add('Access-Control-Allow-Origin',
                             'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,X-Requested-With,Accept,Origin')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,PUT,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    # Create an endpoint to check the health of the application
    @app.route('/health')
    def health():
        return {'status': 'ok'}

    # Create an endpoint to get a test token
    @app.route('/test-token')
    def test_token():
        # Create a token for user ID 1 (admin)
        access_token = create_access_token(identity=1)
        return jsonify(access_token=access_token)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
