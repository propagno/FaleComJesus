from .database import db, BaseModel
from app.utils.security import encrypt_api_key, decrypt_api_key


class APIKey(db.Model, BaseModel):
    """API key model for storing encrypted API keys for different LLM providers"""
    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 'openai', 'anthropic', 'google', etc.
    provider = db.Column(db.String(50), nullable=False)
    key_encrypted = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_used = db.Column(db.DateTime, nullable=True)
    use_count = db.Column(db.Integer, default=0)

    # Relationships
    user = db.relationship("User", back_populates="api_keys")

    def __init__(self, user_id, provider, api_key):
        self.user_id = user_id
        self.provider = provider
        self.set_api_key(api_key)

    def set_api_key(self, api_key):
        """Encrypt and set the API key"""
        self.key_encrypted = encrypt_api_key(api_key)

    def get_api_key(self):
        """Decrypt and return the API key"""
        if not self.key_encrypted:
            return None
        return decrypt_api_key(self.key_encrypted)

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'provider': self.provider,
            'is_active': self.is_active,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_by_user_and_provider(cls, user_id, provider):
        """Get API key by user and provider"""
        return cls.query.filter_by(user_id=user_id, provider=provider, is_active=True).first()

    @classmethod
    def get_all_by_user(cls, user_id):
        """Get all API keys for a user"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.provider).all()
