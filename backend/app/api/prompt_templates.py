from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from flask_cors import cross_origin
from app.models.prompt_template import PromptTemplate
from app.models.database import db
from app.models.user import User
from app.utils.limiter import limiter
from app.utils.logger import logger

# Blueprint definition
prompt_templates_bp = Blueprint(
    'prompt_templates', __name__, url_prefix='/api/prompts')

# Schema definitions


class PromptTemplateSchema(Schema):
    """Schema for prompt template validation"""
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    description = fields.Str(required=False, allow_none=True)
    template = fields.Str(required=True)


class PromptTemplateResponseSchema(Schema):
    """Schema for prompt template responses"""
    id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str(allow_none=True)
    template = fields.Str()
    is_system = fields.Bool()
    user_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class PromptTemplateListResponseSchema(Schema):
    """Schema for list of prompt templates"""
    templates = fields.List(fields.Nested(PromptTemplateResponseSchema))
    count = fields.Int()

# API endpoints


@prompt_templates_bp.route('', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
@cross_origin()
def get_templates():
    """Get all prompt templates available to the user"""
    user_id = get_jwt_identity()

    # Get all templates (system + user's own)
    templates = PromptTemplate.get_available_templates(user_id)

    # Serialize the response
    response = {
        'templates': [template.to_dict() for template in templates],
        'count': len(templates)
    }

    return jsonify(response), 200


@prompt_templates_bp.route('/<int:template_id>', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
@cross_origin()
def get_template(template_id):
    """Get a specific prompt template"""
    user_id = get_jwt_identity()

    # Find the template
    template = PromptTemplate.query.get(template_id)

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    # Check if the user has access to this template
    if not template.is_system and template.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify(template.to_dict()), 200


@prompt_templates_bp.route('', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
@cross_origin()
def create_template():
    """Create a new prompt template"""
    user_id = get_jwt_identity()

    # Parse and validate the request
    schema = PromptTemplateSchema()

    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400

    # Create new template
    template = PromptTemplate(
        name=data['name'],
        description=data.get('description'),
        template=data['template'],
        is_system=False,
        user_id=user_id
    )

    # Save to database
    db.session.add(template)
    db.session.commit()

    logger.info(f"User {user_id} created new prompt template: {template.id}")

    return jsonify(template.to_dict()), 201


@prompt_templates_bp.route('/<int:template_id>', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
@cross_origin()
def update_template(template_id):
    """Update an existing prompt template"""
    user_id = get_jwt_identity()

    # Find the template
    template = PromptTemplate.query.get(template_id)

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    # Check if the user owns this template
    if template.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    # System templates cannot be modified by users
    if template.is_system:
        return jsonify({'error': 'System templates cannot be modified'}), 403

    # Parse and validate the request
    schema = PromptTemplateSchema()

    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400

    # Update template
    template.name = data['name']
    template.description = data.get('description')
    template.template = data['template']

    # Save to database
    db.session.commit()

    logger.info(f"User {user_id} updated prompt template: {template.id}")

    return jsonify(template.to_dict()), 200


@prompt_templates_bp.route('/<int:template_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("10 per minute")
@cross_origin()
def delete_template(template_id):
    """Delete a prompt template"""
    user_id = get_jwt_identity()

    # Find the template
    template = PromptTemplate.query.get(template_id)

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    # Check if the user owns this template
    if template.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    # System templates cannot be deleted by users
    if template.is_system:
        return jsonify({'error': 'System templates cannot be deleted'}), 403

    # Delete the template
    db.session.delete(template)
    db.session.commit()

    logger.info(f"User {user_id} deleted prompt template: {template_id}")

    return jsonify({'message': 'Template deleted successfully'}), 200

# Admin endpoint to create system templates


@prompt_templates_bp.route('/system', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
@cross_origin()
def create_system_template():
    """Create a new system template (admin only)"""
    user_id = get_jwt_identity()

    # Check if user is admin
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403

    # Parse and validate the request
    schema = PromptTemplateSchema()

    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400

    # Create new system template
    template = PromptTemplate(
        name=data['name'],
        description=data.get('description'),
        template=data['template'],
        is_system=True,
        user_id=None  # System templates don't belong to any user
    )

    # Save to database
    db.session.add(template)
    db.session.commit()

    logger.info(f"Admin {user_id} created new system template: {template.id}")

    return jsonify(template.to_dict()), 201

# Adicionar endpoint OPTIONS genérico para lidar com preflight requests


@prompt_templates_bp.route('', methods=['OPTIONS'])
@cross_origin()
def templates_options():
    resp = Response('')
    resp.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp


@prompt_templates_bp.route('/<int:template_id>', methods=['OPTIONS'])
@cross_origin()
def template_options(template_id):
    resp = Response('')
    resp.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, PUT, DELETE, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp


@prompt_templates_bp.route('/system', methods=['OPTIONS'])
@cross_origin()
def system_template_options():
    resp = Response('')
    resp.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp
