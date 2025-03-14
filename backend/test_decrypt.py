#!/usr/bin/env python
"""
Script to test API key decryption.
"""
from app import create_app
from app.models.api_key import APIKey
from app.utils.security import decrypt_api_key


def test_decrypt():
    """Test API key decryption."""
    app = create_app()
    with app.app_context():
        # Obter a chave OpenAI do usuário admin
        api_key = APIKey.get_by_user_and_provider(1, 'openai')

        if not api_key:
            print('Nenhuma API Key OpenAI encontrada')
            return

        print(f'API Key ID: {api_key.id}')
        print(f'Provider: {api_key.provider}')

        # Tentar descriptografar
        try:
            encrypted = api_key.key_encrypted
            print(f'\nChave criptografada: {encrypted[:10]}...')

            # Tentar descriptografar
            decrypted = decrypt_api_key(encrypted)
            print(f'\nChave descriptografada: {decrypted[:5]}...')
            print('Descriptografia bem-sucedida!')
        except Exception as e:
            print(f'\nErro ao descriptografar: {str(e)}')

            # Se o erro for de padding, tente remover a chave e criar uma nova
            if 'padding' in str(e).lower():
                print('\nDetectado erro de padding. Recriando a chave...')

                # Remover a chave problemática
                try:
                    api_key_id = api_key.id
                    APIKey.query.filter_by(id=api_key_id).delete()
                    app.extensions['sqlalchemy'].db.session.commit()
                    print(f'Chave anterior removida (ID: {api_key_id})')

                    # Criar uma nova chave de exemplo
                    new_key = APIKey(
                        user_id=1,
                        provider='openai',
                        api_key='sk-exemplo123456789abcdefghijklmnopqrstuvwxyz'
                    )
                    app.extensions['sqlalchemy'].db.session.add(new_key)
                    app.extensions['sqlalchemy'].db.session.commit()
                    print(f'Nova chave criada com ID: {new_key.id}')

                    # Verificar se a nova chave pode ser descriptografada
                    try:
                        decrypted = new_key.get_api_key()
                        print(
                            f'Nova chave pode ser descriptografada: {decrypted[:5]}...')
                    except Exception as e2:
                        print(f'Erro ao descriptografar nova chave: {str(e2)}')

                except Exception as db_error:
                    print(f'Erro ao atualizar banco de dados: {str(db_error)}')


if __name__ == "__main__":
    test_decrypt()
