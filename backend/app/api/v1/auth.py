from flask import Blueprint, request, jsonify, url_for, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from datetime import datetime
from app.models import User, db
from app.schemas.user import UserSchema
from app.utils.security import validate_password
from app.utils.email_sender import send_password_reset_email

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()

    # Check if user already exists
    if User.get_by_email(data.get('email')):
        return jsonify({'message': 'Email already registered'}), 409

    # Validate password
    password = data.get('password')
    if not validate_password(password):
        return jsonify({'message': 'Password does not meet security requirements'}), 400

    # Create new user
    user = User(
        email=data.get('email'),
        password=password,
        first_name=data.get('first_name'),
        last_name=data.get('last_name')
    )
    user.save()

    # Generate tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': UserSchema().dump(user)
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user"""
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')

    # Find user by email
    user = User.get_by_email(email)

    # Check if user exists and password is correct
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401

    # Check if user is active
    if not user.is_active:
        return jsonify({'message': 'Account is deactivated'}), 403

    # Generate tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': UserSchema().dump(user)
    }), 200


@auth_bp.route('/oauth/callback', methods=['POST'])
def oauth_callback():
    """Handle OAuth login callback"""
    data = request.get_json()
    provider = data.get('provider')
    oauth_id = data.get('oauth_id')
    email = data.get('email')

    if not provider or not oauth_id or not email:
        return jsonify({'message': 'Missing OAuth data'}), 400

    # Find user by OAuth ID or email
    user = User.get_by_oauth(provider, oauth_id) or User.get_by_email(email)

    if not user:
        # Create new user if not exists
        user = User(
            email=email,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            oauth_provider=provider,
            oauth_id=oauth_id
        )
        user.save()
    elif not user.oauth_id:
        # Update existing user with OAuth info
        user.oauth_provider = provider
        user.oauth_id = oauth_id
        db.session.commit()

    # Generate tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'OAuth login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': UserSchema().dump(user)
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)

    return jsonify({
        'access_token': access_token
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout a user (client should discard tokens)"""
    # In a more complex implementation, we would blacklist the token
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request a password reset"""
    data = request.get_json()
    email = data.get('email', '')

    if not email:
        return jsonify({'message': 'Email is required'}), 400

    # Find user by email
    user = User.get_by_email(email)

    # Even if user doesn't exist, return success to prevent email enumeration
    if not user:
        return jsonify({'message': 'If your email is registered, you will receive instructions to reset your password'}), 200

    # Generate reset token
    reset_token = user.generate_reset_token()

    # Create reset URL
    frontend_url = current_app.config.get(
        'FRONTEND_URL', 'http://localhost:3000')
    reset_url = f"{frontend_url}/reset-password?token={reset_token}"

    # Send email
    email_sent = send_password_reset_email(user, reset_url)

    if email_sent:
        return jsonify({
            'message': 'Password reset instructions have been sent to your email'
        }), 200
    else:
        return jsonify({
            'message': 'Failed to send password reset email. Please try again later.'
        }), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    data = request.get_json()
    token = data.get('token', '')
    new_password = data.get('password', '')

    if not token or not new_password:
        return jsonify({'message': 'Token and new password are required'}), 400

    # Validate new password
    if not validate_password(new_password):
        return jsonify({'message': 'Password does not meet security requirements'}), 400

    # Find user by token
    user = User.get_by_reset_token(token)

    if not user:
        return jsonify({'message': 'Invalid or expired token'}), 400

    # Reset password
    user.set_password(new_password)
    user.clear_reset_token()

    return jsonify({'message': 'Password has been reset successfully'}), 200


@auth_bp.route('/verify-reset-token', methods=['POST'])
def verify_reset_token():
    """Verify if reset token is valid"""
    data = request.get_json()
    token = data.get('token', '')

    if not token:
        return jsonify({'message': 'Token is required'}), 400

    # Find user by token
    user = User.get_by_reset_token(token)

    if user:
        return jsonify({'valid': True}), 200
    else:
        return jsonify({'valid': False}), 200
