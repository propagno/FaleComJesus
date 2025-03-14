from flask import Blueprint, request, jsonify, redirect, url_for
from flask.views import MethodView
from marshmallow import Schema, fields, validate, ValidationError
from flask_jwt_extended import create_access_token

from app.models.user import User
from app.utils.security import generate_jwt_token, token_required, validate_password, verify_jwt_token
from app.utils.rate_limit import rate_limit
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


class UserRegisterSchema(Schema):
    """Schema for user registration"""
    email = fields.Email(required=True)
    password = fields.String(required=True)
    first_name = fields.String(required=False, allow_none=True)
    last_name = fields.String(required=False, allow_none=True)


class UserLoginSchema(Schema):
    """Schema for user login"""
    email = fields.Email(required=True)
    password = fields.String(required=True)


class AuthResource(MethodView):
    """Authentication resource"""

    @rate_limit(limit=10, period=60, key_prefix='auth_register')
    def register(self):
        """Register a new user"""
        # Validate request data
        schema = UserRegisterSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({'error': 'Validation error', 'details': err.messages}), 400

        # Check if email already exists
        if User.get_by_email(data['email']):
            return jsonify({'error': 'Registration failed', 'message': 'Email already exists'}), 400

        # Validate password
        if not validate_password(data['password']):
            return jsonify({
                'error': 'Validation error',
                'message': 'Password must be at least 8 characters and include uppercase, lowercase, digit, and special character'
            }), 400

        # Create user
        user = User(
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        user.save()

        # Generate token
        token = generate_jwt_token(user.id)

        # Return response
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict(),
            'token': token
        }), 201

    @rate_limit(limit=20, period=60, key_prefix='auth_login')
    def login(self):
        """Login a user"""
        # Validate request data
        schema = UserLoginSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({'error': 'Validation error', 'details': err.messages}), 400

        # Get user
        user = User.get_by_email(data['email'])

        # Check if user exists and password is correct
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Authentication failed', 'message': 'Invalid credentials'}), 401

        # Update last login
        user.last_login = datetime.utcnow()
        user.save()

        # Generate token using Flask-JWT-Extended
        token = create_access_token(identity=user.id)

        # Return response
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': token
        }), 200

    @token_required
    def profile(self, user_id):
        """Get user profile"""
        # Get user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Return user profile
        return jsonify({
            'user': user.to_dict()
        }), 200


# Register the authentication resource
auth_view = AuthResource()
auth_bp.add_url_rule(
    '/register', view_func=auth_view.register, methods=['POST'])
auth_bp.add_url_rule('/login', view_func=auth_view.login, methods=['POST'])
auth_bp.add_url_rule('/profile', view_func=auth_view.profile, methods=['GET'])

# Adicionar endpoint de refresh para compatibilidade


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Compatibilidade com endpoint v1 de refresh"""
    # Obtém o token de auth do cabeçalho
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    else:
        # Também aceita refresh_token no corpo da requisição
        refresh_token = request.json.get('refresh_token')
        if refresh_token:
            token = refresh_token
        else:
            return jsonify({'message': 'Refresh token is missing'}), 401

    # Verifica se o token é válido
    try:
        # Tenta verificar com SECRET_KEY
        user_id = verify_jwt_token(token)
        if not user_id:
            return jsonify({'message': 'Invalid refresh token'}), 401

        # Cria um novo token com SECRET_KEY para manter compatibilidade
        new_token = generate_jwt_token(user_id)
        return jsonify({'access_token': new_token}), 200

    except Exception as e:
        # Se falhar, tenta redirecionar para o endpoint v1
        try:
            from app.api.v1.auth import refresh as v1_refresh
            return v1_refresh()
        except Exception as e2:
            return jsonify({'message': f'Error refreshing token: {str(e2)}'}), 401
