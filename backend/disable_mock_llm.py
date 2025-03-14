#!/usr/bin/env python
"""
Script para desativar o modo de simulação LLM no ambiente de desenvolvimento.
"""
import os
import logging
from app import create_app

# Configurar logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def disable_mock_llm():
    """Desativa o modo de simulação LLM."""
    try:
        # Definir a variável de ambiente USE_MOCK_LLM como False
        os.environ['USE_MOCK_LLM'] = 'False'

        # Criar a aplicação para verificar as configurações
        app = create_app()

        with app.app_context():
            # Verificar se a configuração foi aplicada
            use_mock_llm = app.config.get('USE_MOCK_LLM', True)
            env = app.config.get('ENV', 'unknown')

            logger.info(f"Ambiente: {env}")
            logger.info(f"Modo de simulação LLM: {use_mock_llm}")

            if not use_mock_llm:
                logger.info("✅ Modo de simulação LLM desativado com sucesso!")
                return True
            else:
                logger.error(
                    "❌ Não foi possível desativar o modo de simulação LLM.")
                return False

    except Exception as e:
        logger.error(f"Erro ao desativar o modo de simulação LLM: {str(e)}")
        return False


if __name__ == "__main__":
    success = disable_mock_llm()
    if success:
        logger.info("Para aplicar as alterações, reinicie o servidor backend:")
        logger.info("  docker-compose restart backend")
    else:
        logger.error("Falha ao desativar o modo de simulação LLM.")
