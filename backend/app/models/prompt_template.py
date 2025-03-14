from app.models.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime


class PromptTemplate(db.Model, BaseModel):
    """
    Model for storing prompt templates used in the system.
    """
    __tablename__ = 'prompt_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    template = Column(Text, nullable=False)
    is_system = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="prompt_templates")

    def to_dict(self):
        """
        Convert the model to a dictionary for API responses.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'template': self.template,
            'is_system': self.is_system,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_system_templates(cls):
        """
        Get all system templates available to all users.
        """
        return cls.query.filter_by(is_system=True).all()

    @classmethod
    def get_user_templates(cls, user_id):
        """
        Get all templates created by a specific user.
        """
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def get_available_templates(cls, user_id):
        """
        Get all templates available to a user (system templates + user templates).
        """
        system_templates = cls.get_system_templates()
        user_templates = cls.get_user_templates(user_id)
        return system_templates + user_templates
