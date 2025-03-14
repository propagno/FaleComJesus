from .database import db, BaseModel
from sqlalchemy.orm import relationship


class Note(db.Model, BaseModel):
    """Model for storing user notes and reflections"""
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(255), nullable=True)
    is_favorite = db.Column(db.Boolean, default=False)
    daily_message_id = db.Column(db.Integer, db.ForeignKey(
        'daily_messages.id'), nullable=True)

    # Relationships
    user = relationship("User", back_populates="notes")
    daily_message = relationship("DailyMessage", back_populates="notes")

    def __init__(self, user_id, content, title=None, is_favorite=False, daily_message_id=None):
        self.user_id = user_id
        self.content = content
        self.title = title
        self.is_favorite = is_favorite
        self.daily_message_id = daily_message_id

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'title': self.title,
            'is_favorite': self.is_favorite,
            'daily_message_id': self.daily_message_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_by_user(cls, user_id, limit=None):
        """Get notes for a specific user"""
        query = cls.query.filter_by(
            user_id=user_id).order_by(cls.created_at.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    @classmethod
    def get_favorites_by_user(cls, user_id):
        """Get favorite notes for a specific user"""
        return cls.query.filter_by(user_id=user_id, is_favorite=True).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_recent_by_user(cls, user_id, limit=2):
        """Get the most recent notes for a specific user"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).limit(limit).all()
