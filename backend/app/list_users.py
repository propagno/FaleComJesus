#!/usr/bin/env python
"""
Script to list all users in the system.
"""
from app.models.user import User
from app import create_app
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def list_users():
    """List all users in the system."""
    app = create_app()
    with app.app_context():
        users = User.query.all()
        print('Usuários:')
        for user in users:
            print(f'ID: {user.id}, Email: {user.email}')


if __name__ == "__main__":
    list_users()
