from .database import db, BaseModel
from sqlalchemy.orm import relationship
import json


class Conversation(db.Model, BaseModel):
    """Model for storing user chat conversations"""
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation",
                            cascade="all, delete-orphan", order_by="Message.created_at")

    def __init__(self, user_id, title=None):
        self.user_id = user_id
        self.title = title or "Nova conversa"

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'messages': [message.to_dict() for message in self.messages]
        }

    @classmethod
    def get_by_user(cls, user_id, limit=10):
        """Get conversations for a specific user"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.updated_at.desc()).limit(limit).all()

    @classmethod
    def get_by_user_with_messages(cls, user_id, conversation_id):
        """Get a conversation with all messages"""
        return cls.query.filter_by(user_id=user_id, id=conversation_id).first()
