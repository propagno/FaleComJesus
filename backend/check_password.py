#!/usr/bin/env python
"""
Script to check user password.
"""
from app import create_app
from app.models.user import User


def check_password():
    """Check user password."""
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email='admin@example.com').first()
        if user:
            print(f'Usuário: {user.email}')
            print(f'Senha hash: {user.password_hash}')
        else:
            print('Usuário não encontrado')


if __name__ == "__main__":
    check_password()
