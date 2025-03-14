#!/usr/bin/env python
"""
Script para corrigir chaves de API com problemas de padding.
Este script remove todas as chaves de API existentes e cria uma nova chave de exemplo para OpenAI.
"""
from app import create_app
from app.models.api_key import APIKey
from app.utils.security import encrypt_api_key
from app.models.database import db
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fix_api_keys():
    """Corrige as chaves de API com problemas de padding."""
    app = create_app()
    with app.app_context():
        try:
            # Listar todas as chaves existentes
            existing_keys = APIKey.query.all()
            logger.info(f"Encontradas {len(existing_keys)} chaves de API")

            # Remover todas as chaves existentes
            for key in existing_keys:
                logger.info(
                    f"Removendo chave ID {key.id} para o provider {key.provider}")
                db.session.delete(key)

            db.session.commit()
            logger.info("Todas as chaves foram removidas com sucesso")

            # Criar uma nova chave de exemplo para OpenAI (não é uma chave real)
            exemplo_key = "exemplo-chave-nao-real-123456789"
            new_key = APIKey(
                user_id=1,  # ID do usuário admin
                provider='openai',
                api_key=exemplo_key
            )

            db.session.add(new_key)
            db.session.commit()
            logger.info(f"Nova chave criada com ID: {new_key.id}")

            # Verificar se a nova chave pode ser descriptografada
            try:
                decrypted = new_key.get_api_key()
                logger.info(
                    f"Nova chave pode ser descriptografada: {decrypted[:5]}...")
                return True
            except Exception as e:
                logger.error(f"Erro ao descriptografar nova chave: {str(e)}")
                return False

        except Exception as e:
            logger.error(f"Erro ao corrigir chaves de API: {str(e)}")
            db.session.rollback()
            return False


if __name__ == "__main__":
    success = fix_api_keys()
    if success:
        logger.info("Correção de chaves de API concluída com sucesso!")
    else:
        logger.error("Falha na correção de chaves de API.")
