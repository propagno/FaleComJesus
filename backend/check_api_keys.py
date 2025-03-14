#!/usr/bin/env python
"""
Script to check API keys for a user.
"""
from app import create_app
from app.models.api_key import APIKey


def check_api_keys():
    """Check API keys for a user."""
    app = create_app()
    with app.app_context():
        # Verificar as chaves do usuário admin (ID 1)
        api_keys = APIKey.get_all_by_user(1)

        if api_keys:
            print(f'API Keys encontradas para o usuário admin:')
            for key in api_keys:
                print(
                    f'ID: {key.id}, Provider: {key.provider}, Ativa: {key.is_active}')
                print(f'Criada em: {key.created_at}')
                # Não exibimos a chave por segurança
        else:
            print('Nenhuma API Key encontrada para o usuário admin')

        # Verificar especificamente por chave OpenAI
        openai_key = APIKey.get_by_user_and_provider(1, 'openai')
        if openai_key:
            print(f'\nAPI Key OpenAI encontrada!')
        else:
            print(f'\nNenhuma API Key OpenAI encontrada para o usuário admin')


if __name__ == "__main__":
    check_api_keys()
