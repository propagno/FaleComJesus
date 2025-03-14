import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Configuração do logger
logger = logging.getLogger('falecomjesus')
logger.setLevel(logging.INFO)

# Handler para console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Handler para arquivo (opcional, ativado se LOG_FILE estiver definido)
log_file = os.environ.get('LOG_FILE')
if log_file:
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10485760, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

# Evitar propagação de logs para outros handlers
logger.propagate = False
