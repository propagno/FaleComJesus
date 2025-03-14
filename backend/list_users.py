#!/usr/bin/env python
"""
Script to list all users in the system.
"""
from app import create_app
from app.models.user import User


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
