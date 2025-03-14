from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declared_attr

# Initialize SQLAlchemy
db = SQLAlchemy()


class BaseModel:
    """Base model class that includes common functionality for all models"""

    # Common columns for all models
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)

    @declared_attr
    def __tablename__(cls):
        """Generate __tablename__ automatically"""
        return cls.__name__.lower()

    def save(self):
        """Save the model instance to the database"""
        db.session.add(self)
        db.session.commit()
        return self

    def update(self, **kwargs):
        """Update the model instance with the given values"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
        return self

    def delete(self):
        """Delete the model instance from the database"""
        db.session.delete(self)
        db.session.commit()
        return True

    @classmethod
    def create(cls, **kwargs):
        """Create a new model instance with the given values"""
        instance = cls(**kwargs)
        instance.save()
        return instance

    @classmethod
    def get_by_id(cls, id):
        """Get a model instance by its ID"""
        return cls.query.get(id)

    @classmethod
    def get_all(cls):
        """Get all model instances"""
        return cls.query.all()

    @classmethod
    def filter_by(cls, **kwargs):
        """Filter model instances by the given values"""
        return cls.query.filter_by(**kwargs).all()
