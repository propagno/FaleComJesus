from marshmallow import Schema, fields, validate, post_load
from app.models import DailyMessage


class DailyMessageSchema(Schema):
    """Schema for serializing and deserializing DailyMessage objects"""
    id = fields.Int(dump_only=True)
    message = fields.Str(required=True)
    bible_verse = fields.Str(required=True)
    bible_reference = fields.Str(required=True)
    date = fields.Date(required=True)
    created_at = fields.DateTime(dump_only=True)

    @post_load
    def make_daily_message(self, data, **kwargs):
        """Create a DailyMessage instance from validated data"""
        return DailyMessage(**data)
