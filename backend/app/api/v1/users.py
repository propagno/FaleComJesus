from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, db
from app.schemas.user import UserSchema
from app.utils.security import validate_password

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get the current user's profile"""
    user_id = get_jwt_identity()
    user = User.get_by_id(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify(UserSchema().dump(user)), 200


@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update the current user's profile"""
    user_id = get_jwt_identity()
    user = User.get_by_id(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()

    # Update allowed fields
    if 'first_name' in data:
        user.first_name = data['first_name']

    if 'last_name' in data:
        user.last_name = data['last_name']

    # Handle password change
    if 'password' in data:
        if not validate_password(data['password']):
            return jsonify({'message': 'Password does not meet security requirements'}), 400

        user.set_password(data['password'])

    try:
        db.session.commit()
        return jsonify(UserSchema().dump(user)), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400


@users_bp.route('/me/deactivate', methods=['POST'])
@jwt_required()
def deactivate_account():
    """Deactivate the current user's account"""
    user_id = get_jwt_identity()
    user = User.get_by_id(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.is_active = False

    try:
        db.session.commit()
        return jsonify({'message': 'Account deactivated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400
