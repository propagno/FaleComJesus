from .database import db, BaseModel
from sqlalchemy.orm import relationship
from datetime import date


class DailyMessage(db.Model, BaseModel):
    """Daily inspirational message with Bible verse"""
    __tablename__ = 'daily_messages'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    bible_verse = db.Column(db.String(255), nullable=False)
    bible_reference = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, default=date.today,
                     nullable=False, unique=True, index=True)

    # Relationships
    notes = relationship("Note", back_populates="daily_message")

    def __init__(self, message, bible_verse, bible_reference, date=None):
        self.message = message
        self.bible_verse = bible_verse
        self.bible_reference = bible_reference
        if date:
            self.date = date

    def to_dict(self):
        """Convert daily message to dictionary for serialization"""
        return {
            'id': self.id,
            'message': self.message,
            'bible_verse': self.bible_verse,
            'bible_reference': self.bible_reference,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def get_by_date(cls, date_obj):
        """Get daily message for a specific date"""
        return cls.query.filter_by(date=date_obj).first()

    @classmethod
    def get_today(cls):
        """Get today's daily message"""
        return cls.get_by_date(date.today())
