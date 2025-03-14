from marshmallow import Schema, fields, validate, post_load
from app.models import BibleVerse


class BibleVerseSchema(Schema):
    """Schema for serializing and deserializing BibleVerse objects"""
    id = fields.Int(dump_only=True)
    book = fields.Str(required=True)
    chapter = fields.Int(required=True)
    verse = fields.Int(required=True)
    text = fields.Str(required=True)
    translation = fields.Str(default='NVI')
    reference = fields.Str(dump_only=True)

    @post_load
    def make_bible_verse(self, data, **kwargs):
        """Create a BibleVerse instance from validated data"""
        return BibleVerse(**data)
