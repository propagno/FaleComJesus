from marshmallow import Schema, fields, validate, post_load
from app.models import User


class UserSchema(Schema):
    """Schema for serializing and deserializing User objects"""
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(
        load_only=True, validate=validate.Length(min=8, max=100))
    first_name = fields.Str(validate=validate.Length(max=64))
    last_name = fields.Str(validate=validate.Length(max=64))
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True)

    @post_load
    def make_user(self, data, **kwargs):
        """Create a User instance from validated data"""
        return User(**data)
