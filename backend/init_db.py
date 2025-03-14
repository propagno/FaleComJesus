from app.models.api_key import APIKey
from app.models.note import Note
from app.models.bible_verse import BibleVerse
from app.models.daily_message import DailyMessage
from app.models.user import User
from app.models.database import db
from app import create_app
import os
import sys
from flask import Flask

# Adiciona o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


app = create_app()


def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    with app.app_context():
        print("Criando tabelas no banco de dados...")
        db.create_all()
        print("Tabelas criadas com sucesso!")


if __name__ == '__main__':
    init_db()
