from .database import db, BaseModel
from sqlalchemy.orm import relationship
import json


class Message(db.Model, BaseModel):
    """Model for storing individual chat messages"""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey(
        'conversations.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(50), nullable=False)  # 'user' or 'bot'
    # JSON data for additional info
    meta_data = db.Column(db.Text, nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __init__(self, conversation_id, content, sender, metadata=None):
        self.conversation_id = conversation_id
        self.content = content
        self.sender = sender
        if metadata:
            self.set_metadata(metadata)

    def set_metadata(self, metadata):
        """Set metadata as JSON string"""
        if isinstance(metadata, dict):
            self.meta_data = json.dumps(metadata)
        else:
            self.meta_data = metadata

    def get_metadata(self):
        """Get metadata as dictionary"""
        if not self.meta_data:
            return {}
        try:
            return json.loads(self.meta_data)
        except:
            return {}

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'content': self.content,
            'sender': self.sender,
            'metadata': self.get_metadata(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
