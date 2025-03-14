from marshmallow import Schema, fields, validate, post_load
from app.models import Note


class NoteSchema(Schema):
    """Schema for serializing and deserializing Note objects"""
    id = fields.Int(dump_only=True)
    content = fields.Str(required=True)
    title = fields.Str(allow_none=True)
    is_favorite = fields.Boolean(default=False)
    user_id = fields.Int(required=True)
    daily_message_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @post_load
    def make_note(self, data, **kwargs):
        """Create a Note instance from validated data"""
        return Note(**data)
