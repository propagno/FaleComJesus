#!/usr/bin/env python
"""
Script to reset user password.
"""
from app import create_app
from app.models.user import User
from app.models.database import db


def reset_password():
    """Reset user password."""
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email='admin@example.com').first()
        if user:
            print(f'Usuário: {user.email}')
            print(f'Senha hash antiga: {user.password_hash}')

            # Define a nova senha
            new_password = 'admin123'
            user.set_password(new_password)

            # Salva as alterações
            db.session.commit()

            print(f'Senha alterada com sucesso!')
            print(f'Nova senha: {new_password}')
            print(f'Novo hash: {user.password_hash}')
        else:
            print('Usuário não encontrado')


if __name__ == "__main__":
    reset_password()
