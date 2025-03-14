from flask import Blueprint, request, jsonify
from flask.views import MethodView
from marshmallow import Schema, fields, ValidationError
from flask_cors import cross_origin

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.utils.security import token_required
from app.utils.rate_limit import rate_limit

# Inicializar o blueprint
conversations_bp = Blueprint(
    'conversations', __name__, url_prefix='/api/conversations')


# Schemas para validação e serialização
class MessageSchema(Schema):
    """Schema para mensagens"""
    id = fields.Int(dump_only=True)
    content = fields.Str(required=True)
    sender = fields.Str(required=True)
    metadata = fields.Dict(missing={})
    created_at = fields.DateTime(dump_only=True)


class ConversationSchema(Schema):
    """Schema para conversas"""
    id = fields.Int(dump_only=True)
    title = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    messages = fields.List(fields.Nested(MessageSchema()), dump_only=True)


class ConversationListResponse(Schema):
    """Schema para resposta da listagem de conversas"""
    conversations = fields.List(fields.Nested(ConversationSchema()))
    count = fields.Int()


class ConversationResource(MethodView):
    """Recurso para gerenciar conversas"""

    def options(self, conversation_id=None):
        """Responde a requisições OPTIONS (preflight) para CORS"""
        resp = jsonify({'success': True})
        resp.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

    @token_required
    @rate_limit(limit=100, period=60, key_prefix='conversations_list')
    def get(self, user_id, conversation_id=None):
        """Obter conversas do usuário"""

        # Verificar se o usuário existe
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        # Se um ID de conversa for fornecido, retornar conversa específica
        if conversation_id:
            conversation = Conversation.get_by_user_with_messages(
                user_id, conversation_id)
            if not conversation:
                return jsonify({'error': 'Conversa não encontrada'}), 404

            return jsonify(conversation.to_dict()), 200

        # Caso contrário, listar todas as conversas do usuário
        conversations = Conversation.get_by_user(user_id)

        # Serializar a resposta
        response = {
            'conversations': [conv.to_dict() for conv in conversations],
            'count': len(conversations)
        }

        return jsonify(response), 200

    @token_required
    @rate_limit(limit=20, period=60, key_prefix='conversations_create')
    def post(self, user_id):
        """Criar uma nova conversa"""

        # Verificar se o usuário existe
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        # Obter dados da requisição
        data = request.json or {}
        title = data.get('title', 'Nova conversa')

        # Criar nova conversa
        conversation = Conversation(user_id=user_id, title=title)
        conversation.save()

        return jsonify({
            'message': 'Conversa criada com sucesso',
            'conversation': conversation.to_dict()
        }), 201

    @token_required
    @rate_limit(limit=20, period=60, key_prefix='conversations_update')
    def put(self, user_id, conversation_id):
        """Atualizar título da conversa"""

        # Verificar se o usuário existe
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        # Verificar se a conversa existe e pertence ao usuário
        conversation = Conversation.query.filter_by(
            id=conversation_id, user_id=user_id).first()
        if not conversation:
            return jsonify({'error': 'Conversa não encontrada'}), 404

        # Obter dados da requisição
        data = request.json or {}
        title = data.get('title')

        if title:
            conversation.title = title
            conversation.save()

        return jsonify({
            'message': 'Conversa atualizada com sucesso',
            'conversation': conversation.to_dict()
        }), 200

    @token_required
    @rate_limit(limit=20, period=60, key_prefix='conversations_delete')
    def delete(self, user_id, conversation_id):
        """Excluir uma conversa"""

        # Verificar se o usuário existe
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        # Verificar se a conversa existe e pertence ao usuário
        conversation = Conversation.query.filter_by(
            id=conversation_id, user_id=user_id).first()
        if not conversation:
            return jsonify({'error': 'Conversa não encontrada'}), 404

        # Excluir conversa (isso também exclui todas as mensagens devido à relação cascade)
        conversation.delete()

        return jsonify({
            'message': 'Conversa excluída com sucesso'
        }), 200


class MessageResource(MethodView):
    """Recurso para gerenciar mensagens de uma conversa"""

    def options(self, conversation_id):
        """Responde a requisições OPTIONS (preflight) para CORS"""
        resp = jsonify({'success': True})
        resp.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

    @token_required
    @rate_limit(limit=20, period=60, key_prefix='messages_create')
    def post(self, user_id, conversation_id):
        """Adicionar uma nova mensagem à conversa"""

        # Verificar se o usuário existe
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        # Verificar se a conversa existe e pertence ao usuário
        conversation = Conversation.query.filter_by(
            id=conversation_id, user_id=user_id).first()
        if not conversation:
            return jsonify({'error': 'Conversa não encontrada'}), 404

        # Validar dados da requisição
        schema = MessageSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({'error': 'Erro de validação', 'details': err.messages}), 400

        # Criar nova mensagem
        message = Message(
            conversation_id=conversation_id,
            content=data['content'],
            sender=data['sender'],
            metadata=data.get('metadata')
        )
        message.save()

        # Atualizar timestamp da conversa
        conversation.save()

        return jsonify({
            'message': 'Mensagem adicionada com sucesso',
            'data': message.to_dict()
        }), 201

    @token_required
    @rate_limit(limit=100, period=60, key_prefix='messages_list')
    def get(self, user_id, conversation_id):
        """Obter mensagens de uma conversa"""

        # Verificar se o usuário existe
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        # Verificar se a conversa existe e pertence ao usuário
        conversation = Conversation.query.filter_by(
            id=conversation_id, user_id=user_id).first()
        if not conversation:
            return jsonify({'error': 'Conversa não encontrada'}), 404

        # Serializar mensagens
        messages = [message.to_dict() for message in conversation.messages]

        return jsonify({
            'messages': messages,
            'count': len(messages)
        }), 200


# Registrar recursos
conversation_view = ConversationResource.as_view('conversation_resource')
message_view = MessageResource.as_view('message_resource')

# Rotas para conversas
conversations_bp.add_url_rule(
    '/', view_func=conversation_view, methods=['GET', 'POST', 'OPTIONS'])
conversations_bp.add_url_rule(
    '/<int:conversation_id>', view_func=conversation_view, methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])

# Rotas para mensagens
conversations_bp.add_url_rule(
    '/<int:conversation_id>/messages', view_func=message_view, methods=['GET', 'POST', 'OPTIONS'])
