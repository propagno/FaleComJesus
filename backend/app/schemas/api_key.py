from marshmallow import Schema, fields, validate, ValidationError


class APIKeyCreateSchema(Schema):
    """Schema for creating a new API key"""
    provider = fields.String(
        required=True,
        validate=validate.OneOf([
            'openai', 'anthropic', 'google', 'mistral', 'llama', 'cohere', 'other'
        ])
    )
    api_key = fields.String(required=True)


class APIKeyResponseSchema(Schema):
    """Schema for API key responses (without the actual key)"""
    id = fields.Integer()
    provider = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_used = fields.DateTime(allow_none=True)
    is_active = fields.Boolean()


class APIKeyListSchema(Schema):
    """Schema for listing API keys"""
    api_keys = fields.List(fields.Nested(APIKeyResponseSchema))


class APIKeyDeleteSchema(Schema):
    """Schema for deleting an API key"""
    id = fields.Integer(required=True)
