import pytest
import json
from app import create_app
from app.models.database import db
from app.models.user import User


@pytest.fixture
def client():
    """Test client fixture"""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test_key',
        'JWT_SECRET_KEY': 'test_jwt_key'
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


def test_register_valid_user(client):
    """Test registration with valid user data"""
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'securePassword123',
        'first_name': 'Test',
        'last_name': 'User'
    })

    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['email'] == 'test@example.com'
    assert 'token' in data
    assert data['token'] is not None


def test_register_existing_email(client):
    """Test registration with an existing email"""
    # Create user first
    user = User(email='test@example.com', password='password123',
                first_name='Test', last_name='User')
    with client.application.app_context():
        user.save()

    # Try to register with the same email
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'anotherPassword',
        'first_name': 'Another',
        'last_name': 'User'
    })

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'email already exists' in data['message'].lower()


def test_login_valid_credentials(client):
    """Test login with valid credentials"""
    # Create user first
    with client.application.app_context():
        user = User(email='test@example.com', password='password123',
                    first_name='Test', last_name='User')
        user.save()

    # Login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['email'] == 'test@example.com'
    assert 'token' in data
    assert data['token'] is not None


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    # Create user first
    with client.application.app_context():
        user = User(email='test@example.com', password='password123',
                    first_name='Test', last_name='User')
        user.save()

    # Login with wrong password
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'wrongPassword'
    })

    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data
    assert 'invalid credentials' in data['message'].lower()


def test_get_user_profile(client):
    """Test getting user profile with valid token"""
    # Create user first
    with client.application.app_context():
        user = User(email='test@example.com', password='password123',
                    first_name='Test', last_name='User')
        user.save()
        from app.utils.security import generate_jwt_token
        token = generate_jwt_token(user.id)

    # Get user profile
    response = client.get('/api/auth/profile', headers={
        'Authorization': f'Bearer {token}'
    })

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['email'] == 'test@example.com'
    assert data['user']['first_name'] == 'Test'
    assert data['user']['last_name'] == 'User'


def test_get_user_profile_invalid_token(client):
    """Test getting user profile with invalid token"""
    response = client.get('/api/auth/profile', headers={
        'Authorization': 'Bearer invalidToken'
    })

    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data
    assert 'token' in data['message'].lower()
