from werkzeug.security import generate_password_hash, check_password_hash
from .database import db, BaseModel
from sqlalchemy.orm import relationship
import secrets
from datetime import datetime, timedelta


class User(db.Model, BaseModel):
    """User model for authentication and user data"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=True)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    # 'google', 'facebook', etc.
    oauth_provider = db.Column(db.String(20), nullable=True)
    oauth_id = db.Column(db.String(100), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    # Password reset fields
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    # Relationships
    notes = relationship("Note", back_populates="user",
                         cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user",
                            cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user",
                                 cascade="all, delete-orphan")
    prompt_templates = relationship("PromptTemplate", back_populates="user",
                                    cascade="all, delete-orphan")

    def __init__(self, email, password=None, first_name=None, last_name=None, oauth_provider=None, oauth_id=None):
        self.email = email.lower()
        if password:
            self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.oauth_provider = oauth_provider
        self.oauth_id = oauth_id

    def set_password(self, password):
        """Set password hash from password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        """Generate a password reset token"""
        self.reset_token = secrets.token_hex(16)  # 32 character hex string
        self.reset_token_expires = datetime.utcnow(
        ) + timedelta(hours=1)  # Token expires in 1 hour
        db.session.commit()
        return self.reset_token

    def verify_reset_token(self, token):
        """Verify if reset token is valid"""
        if not self.reset_token or not self.reset_token_expires:
            return False
        if self.reset_token != token:
            return False
        if self.reset_token_expires < datetime.utcnow():
            return False
        return True

    def clear_reset_token(self):
        """Clear reset token after use"""
        self.reset_token = None
        self.reset_token_expires = None
        db.session.commit()

    def to_dict(self):
        """Convert user to dictionary for serialization"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    @classmethod
    def get_by_email(cls, email):
        """Get user by email address"""
        return cls.query.filter_by(email=email.lower()).first()

    @classmethod
    def get_by_oauth(cls, provider, oauth_id):
        """Get user by OAuth provider and ID"""
        return cls.query.filter_by(oauth_provider=provider, oauth_id=oauth_id).first()

    @classmethod
    def get_by_reset_token(cls, token):
        """Get user by reset token"""
        return cls.query.filter_by(reset_token=token).filter(cls.reset_token_expires > datetime.utcnow()).first()
