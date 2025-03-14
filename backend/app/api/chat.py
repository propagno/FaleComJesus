from flask import Blueprint, request, jsonify, current_app
from flask.views import MethodView
from marshmallow import Schema, fields, validate, ValidationError
from flask_jwt_extended import get_jwt_identity
from flask_cors import cross_origin

from app.models.api_key import APIKey
from app.models.user import User
from app.utils.security import token_required
from app.utils.rate_limit import rate_limit
from app.services.llm_service import get_llm_response, LLM_SERVICES
from app.models.conversation import Conversation
from app.models.message import Message
from app.utils.logger import logger
from app.utils.limiter import limiter
from app.utils.jwt_required import jwt_required
from app.utils.prompt_template import PromptTemplate
from app.utils.database import db
from datetime import datetime

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')


class ChatMessageSchema(Schema):
    """Schema for chat message requests"""
    message = fields.Str(required=True)
    provider = fields.Str(required=True)
    model = fields.Str(required=True)
    conversation_id = fields.Int(required=False, allow_none=True)
    template_id = fields.Int(required=False, allow_none=True)
    regenerate = fields.Bool(required=False, default=False)


class ChatResource(MethodView):
    """Chat API resource"""

    @token_required
    @rate_limit(limit=50, period=60, key_prefix='chat_message')
    def post(self, user_id):
        """Process a chat message and get a response"""
        # Validate request data
        schema = ChatMessageSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({'error': 'Validation error', 'details': err.messages}), 400

        # Get the provider and model
        provider = data['provider']
        model = data['model']
        message = data['message']
        conversation_id = data.get('conversation_id')
        template_id = data.get('template_id')
        regenerate = data.get('regenerate', False)

        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get the API key for the provider
        api_key = APIKey.get_by_user_and_provider(user_id, provider)
        if not api_key:
            return jsonify({
                'error': 'API key not found',
                'message': f'You need to add an API key for {provider} to use this service.'
            }), 403

        # Get the decrypted API key
        key = api_key.get_api_key()
        if not key:
            return jsonify({
                'error': 'Invalid API key',
                'message': f'The API key for {provider} is invalid. Please add a valid key.'
            }), 403

        try:
            # Get response from the LLM service
            response = get_llm_response(
                provider=provider,
                model=model,
                api_key=key,
                message=message
            )

            # Update last_used timestamp for the API key
            api_key.last_used = 'NOW()'
            api_key.save()

            return jsonify({
                'response': response,
                'provider': provider,
                'model': model
            }), 200

        except Exception as e:
            current_app.logger.error(f"Error getting LLM response: {str(e)}")
            return jsonify({
                'error': 'LLM service error',
                'message': f'Error communicating with {provider}: {str(e)}'
            }), 500


@chat_bp.route('/message', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
@cross_origin()
def send_message():
    """Send a message to the chat LLM."""
    try:
        # Parse the request data
        schema = ChatMessageSchema()
        data = schema.load(request.json)

        user_message = data['message']
        provider = data['provider']
        model = data['model']
        conversation_id = data.get('conversation_id')
        template_id = data.get('template_id')
        regenerate = data.get('regenerate', False)

        user_id = get_jwt_identity()

        # Validate provider and model
        if provider not in LLM_SERVICES:
            return jsonify({"error": f"Provider '{provider}' not supported"}), 400

        # Get the API key
        api_key = APIKey.query.filter_by(
            user_id=user_id, provider=provider, is_active=True).first()
        if not api_key:
            if current_app.config.get('LLM_SIMULATION_MODE'):
                # In simulation mode, proceed without API key
                logger.warning(
                    f"Simulation mode: Proceeding without API key for {provider}")
            else:
                return jsonify({"error": f"No active API key found for provider '{provider}'"}), 403

        # Get the prompt template if specified
        template = None
        if template_id:
            template_obj = PromptTemplate.query.get(template_id)
            if not template_obj:
                return jsonify({"error": "Template not found"}), 404

            # Check if user has access to this template
            if not template_obj.is_system and template_obj.user_id != user_id:
                return jsonify({"error": "Access denied to this template"}), 403

            template = template_obj.template

        # Handle conversation context
        current_conversation = None
        if conversation_id:
            current_conversation = Conversation.query.filter_by(
                id=conversation_id, user_id=user_id).first()
            if not current_conversation:
                return jsonify({"error": "Conversation not found"}), 404
        else:
            # Create a new conversation
            current_conversation = Conversation(
                user_id=user_id,
                title=user_message[:50] +
                ("..." if len(user_message) > 50 else "")
            )
            db.session.add(current_conversation)
            db.session.commit()

        # Create user message
        user_msg = Message(
            conversation_id=current_conversation.id,
            content=user_message,
            sender="user"
        )
        db.session.add(user_msg)
        db.session.commit()

        # Get the LLM service
        llm_service = LLM_SERVICES[provider](
            api_key=api_key.get_api_key() if api_key else None)

        # Format prompt with template if provided
        formatted_message = user_message
        if template:
            # Get conversation history for context
            conversation_messages = []
            if current_conversation:
                messages = Message.query.filter_by(
                    conversation_id=current_conversation.id).order_by(Message.created_at).all()
                for msg in messages:
                    if msg.id != user_msg.id:  # Skip the message we just added
                        conversation_messages.append({
                            'content': msg.content,
                            'sender': msg.sender
                        })

            formatted_message = llm_service.format_prompt(
                user_message,
                template=template,
                context={
                    'user_id': user_id,
                    'conversation_id': current_conversation.id,
                    'conversation_history': conversation_messages
                }
            )

        # Get response from the LLM
        if current_app.config.get('LLM_SIMULATION_MODE'):
            # In simulation mode, generate a mock response
            logger.info(
                f"Simulation mode: Generating mock response for: {user_message}")
            response_text = f"This is a simulated response for '{user_message}'. Provider: {provider}, Model: {model}"
        else:
            response_text = llm_service.get_response(
                formatted_message, model=model)

        # Create bot message
        bot_msg = Message(
            conversation_id=current_conversation.id,
            content=response_text,
            sender="bot",
            metadata={
                "provider": provider,
                "model": model,
                "regenerated": regenerate
            }
        )
        db.session.add(bot_msg)

        # Update API key usage
        if api_key:
            api_key.last_used = datetime.utcnow()
            api_key.use_count += 1

        db.session.commit()

        return jsonify({
            "response": response_text,
            "conversation_id": current_conversation.id
        }), 200

    except Exception as e:
        logger.error(f"Error in chat API: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500


@chat_bp.route('/test', methods=['GET', 'POST'])
@cross_origin()
def test_endpoint():
    """Test endpoint that doesn't require authentication."""
    return jsonify({
        "status": "success",
        "message": "API está funcionando corretamente!",
        "cors": "Configuração CORS está correta."
    }), 200
