import re
import os
from cryptography.fernet import Fernet
from flask import current_app
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify


def validate_password(password):
    """
    Validate that a password meets security requirements:
    - At least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    """
    if not password or len(password) < 8:
        return False

    # Check for uppercase, lowercase, digit, and special character
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False

    return True


def generate_jwt_token(user_id, expiry_days=1):
    """Generate a JWT token for user authentication"""
    payload = {
        'exp': datetime.utcnow() + timedelta(days=expiry_days),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY'),
        algorithm='HS256'
    )


def verify_jwt_token(token):
    """Verify a JWT token and return the user_id if valid"""
    # Primeiro, tenta decodificar usando a SECRET_KEY (sistema antigo)
    try:
        payload = jwt.decode(token, current_app.config.get(
            'SECRET_KEY'), algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        # Se falhar, tenta com JWT_SECRET_KEY (sistema JWT extended)
        try:
            payload = jwt.decode(token, current_app.config.get(
                'JWT_SECRET_KEY'), algorithms=['HS256'])
            return payload.get('sub') or payload.get('identity')
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None  # Token inválido ou expirado


def token_required(f):
    """Decorator to require valid JWT token for API endpoint"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        user_id = verify_jwt_token(token)
        if not user_id:
            return jsonify({'message': 'Invalid or expired token!'}), 401

        return f(user_id=user_id, *args, **kwargs)

    return decorated


def get_encryption_key():
    """Get or generate the AES-256 encryption key from environment"""
    key = current_app.config.get('ENCRYPTION_KEY')
    if not key:
        # If no key is set, use a derived key from the SECRET_KEY
        # This is not ideal for production, but works for development
        base_key = current_app.config.get('SECRET_KEY', 'fallback_secret_key')
        # Ensure the key is 32 bytes (256 bits) for AES-256
        key = base_key.ljust(32)[:32].encode('utf-8')
    else:
        # If key is provided as base64 string, decode it
        if isinstance(key, str):
            key = base64.b64decode(key)

    return key


def encrypt_api_key(api_key):
    """Encrypt an API key using AES-256"""
    if not api_key:
        return None

    key = get_encryption_key()
    iv = os.urandom(16)  # 16 bytes for AES

    # Pad the data to a multiple of block size
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(api_key.encode('utf-8')) + padder.finalize()

    # Create the cipher with the key and IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                    backend=default_backend())
    encryptor = cipher.encryptor()

    # Encrypt the padded data
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # Store as IV + ciphertext (base64 encoded)
    return base64.b64encode(iv + ciphertext).decode('utf-8')


def decrypt_api_key(encrypted_api_key):
    """Decrypt an API key encrypted with AES-256"""
    if not encrypted_api_key:
        return None

    key = get_encryption_key()

    # Decode the base64 data
    encrypted_data = base64.b64decode(encrypted_api_key)

    # Extract the IV (first 16 bytes) and ciphertext
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    # Create the cipher with the key and IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                    backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the ciphertext
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    # Unpad the data
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    return data.decode('utf-8')


def generate_secure_token(length=32):
    """Generate a secure random token"""
    return os.urandom(length).hex()
