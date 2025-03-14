from flask import Blueprint, request, jsonify, current_app
from flask.views import MethodView
from marshmallow import ValidationError

from app.models.api_key import APIKey
from app.models.user import User
from app.schemas.api_key import (
    APIKeyCreateSchema,
    APIKeyResponseSchema,
    APIKeyListSchema,
    APIKeyDeleteSchema
)
from app.utils.security import token_required
from app.utils.rate_limit import rate_limit

api_keys_bp = Blueprint('api_keys', __name__, url_prefix='/api/keys')


class APIKeyResource(MethodView):
    """API Key resource for managing user API keys"""

    @token_required
    @rate_limit(limit=100, period=60, key_prefix='api_keys_list')
    def get(self, user_id):
        """Get all API keys for the authenticated user"""
        # Get all API keys for the user
        api_keys = APIKey.get_all_by_user(user_id)

        # Serialize API keys
        schema = APIKeyResponseSchema(many=True)
        return jsonify({
            'api_keys': schema.dump(api_keys),
            'count': len(api_keys)
        }), 200

    @token_required
    @rate_limit(limit=20, period=60, key_prefix='api_keys_create')
    def post(self, user_id):
        """Create a new API key for the authenticated user"""
        # Validate request data
        schema = APIKeyCreateSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({'error': 'Validation error', 'details': err.messages}), 400

        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Check if provider already exists for this user
        existing_key = APIKey.get_by_user_and_provider(
            user_id, data['provider'])
        if existing_key:
            # Update existing key instead of creating a new one
            existing_key.set_api_key(data['api_key'])
            existing_key.is_active = True
            existing_key.save()

            # Return updated key
            response_schema = APIKeyResponseSchema()
            return jsonify({
                'message': f"API key for provider '{data['provider']}' updated successfully",
                'api_key': response_schema.dump(existing_key)
            }), 200

        # Create new API key
        api_key = APIKey(
            user_id=user_id,
            provider=data['provider'],
            api_key=data['api_key']
        )
        api_key.save()

        # Return created API key
        response_schema = APIKeyResponseSchema()
        return jsonify({
            'message': f"API key for provider '{data['provider']}' created successfully",
            'api_key': response_schema.dump(api_key)
        }), 201

    @token_required
    @rate_limit(limit=20, period=60, key_prefix='api_keys_delete')
    def delete(self, user_id):
        """Delete an API key for the authenticated user"""
        # Validate request data
        schema = APIKeyDeleteSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({'error': 'Validation error', 'details': err.messages}), 400

        # Get API key
        api_key = APIKey.query.get(data['id'])

        # Check if API key exists and belongs to the user
        if not api_key or api_key.user_id != user_id:
            return jsonify({'error': 'API key not found'}), 404

        # Delete API key
        provider = api_key.provider
        api_key.delete()

        return jsonify({
            'message': f"API key for provider '{provider}' deleted successfully"
        }), 200


# Register the API Key resource
api_key_view = APIKeyResource.as_view('api_key_resource')
api_keys_bp.add_url_rule('', view_func=api_key_view,
                         methods=['GET', 'POST', 'DELETE'])
