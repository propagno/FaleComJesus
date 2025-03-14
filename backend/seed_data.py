from app.models.note import Note
from app.models.bible_verse import BibleVerse
from app.models.daily_message import DailyMessage
from app.models.user import User
from app.models.database import db
from app import create_app
import os
import sys
import datetime
from werkzeug.security import generate_password_hash
from flask import Flask

# Adiciona o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


app = create_app()

# Dados de exemplo
USERS = [
    {
        'email': 'admin@example.com',
        'password': 'Admin123!',
        'first_name': 'Admin',
        'last_name': 'User'
    },
    {
        'email': 'user@example.com',
        'password': 'User123!',
        'first_name': 'Regular',
        'last_name': 'User'
    }
]

DAILY_MESSAGES = [
    {
        'message': 'A fé é a certeza daquilo que esperamos e a prova das coisas que não vemos.',
        'bible_verse': 'Ora, a fé é a certeza daquilo que esperamos e a prova das coisas que não vemos.',
        'bible_reference': 'Hebreus 11:1',
        'date': datetime.date.today()
    },
    {
        'message': 'Confie no Senhor de todo o seu coração e não se apoie em seu próprio entendimento.',
        'bible_verse': 'Confie no Senhor de todo o seu coração e não se apoie em seu próprio entendimento; reconheça o Senhor em todos os seus caminhos, e ele endireitará as suas veredas.',
        'bible_reference': 'Provérbios 3:5-6',
        'date': datetime.date.today() - datetime.timedelta(days=1)
    },
    {
        'message': 'O Senhor é meu pastor, nada me faltará.',
        'bible_verse': 'O Senhor é meu pastor, nada me faltará. Ele me faz repousar em pastos verdejantes. Conduz-me junto às águas refrescantes, restaura as forças de minha alma.',
        'bible_reference': 'Salmos 23:1-3',
        'date': datetime.date.today() - datetime.timedelta(days=2)
    }
]

BIBLE_VERSES = [
    {
        'book': 'João',
        'chapter': 3,
        'verse': 16,
        'text': 'Porque Deus amou o mundo de tal maneira que deu o seu Filho unigênito, para que todo aquele que nele crê não pereça, mas tenha a vida eterna.',
        'translation': 'NVI'
    },
    {
        'book': 'Mateus',
        'chapter': 5,
        'verse': 14,
        'text': 'Vós sois a luz do mundo. Não se pode esconder uma cidade edificada sobre um monte.',
        'translation': 'NVI'
    },
    {
        'book': 'Romanos',
        'chapter': 8,
        'verse': 28,
        'text': 'Sabemos que todas as coisas cooperam para o bem daqueles que amam a Deus, daqueles que são chamados segundo o seu propósito.',
        'translation': 'NVI'
    },
    {
        'book': 'Filipenses',
        'chapter': 4,
        'verse': 13,
        'text': 'Tudo posso naquele que me fortalece.',
        'translation': 'NVI'
    },
    {
        'book': 'Isaías',
        'chapter': 40,
        'verse': 31,
        'text': 'Mas aqueles que esperam no Senhor renovarão as suas forças. Voarão alto como águias; correrão e não ficarão exaustos, andarão e não se cansarão.',
        'translation': 'NVI'
    }
]


def seed_database():
    """Popula o banco de dados com dados de exemplo"""
    with app.app_context():
        print("Iniciando a população do banco de dados...")

        # Cria usuários
        for user_data in USERS:
            if not User.get_by_email(user_data['email']):
                user = User(
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                db.session.add(user)
                print(f"Usuário criado: {user_data['email']}")
            else:
                print(f"Usuário já existe: {user_data['email']}")

        # Cria versículos bíblicos
        for verse_data in BIBLE_VERSES:
            existing_verse = BibleVerse.get_by_reference(
                verse_data['book'],
                verse_data['chapter'],
                verse_data['verse'],
                verse_data['translation']
            )

            if not existing_verse:
                verse = BibleVerse(
                    book=verse_data['book'],
                    chapter=verse_data['chapter'],
                    verse=verse_data['verse'],
                    text=verse_data['text'],
                    translation=verse_data['translation']
                )
                db.session.add(verse)
                print(
                    f"Versículo criado: {verse_data['book']} {verse_data['chapter']}:{verse_data['verse']}")
            else:
                print(
                    f"Versículo já existe: {verse_data['book']} {verse_data['chapter']}:{verse_data['verse']}")

        # Cria mensagens diárias
        for message_data in DAILY_MESSAGES:
            existing_message = DailyMessage.get_by_date(message_data['date'])

            if not existing_message:
                message = DailyMessage(
                    message=message_data['message'],
                    bible_verse=message_data['bible_verse'],
                    bible_reference=message_data['bible_reference'],
                    date=message_data['date']
                )
                db.session.add(message)
                print(f"Mensagem diária criada para: {message_data['date']}")
            else:
                print(
                    f"Mensagem diária já existe para: {message_data['date']}")

        # Cria algumas notas para o usuário de exemplo
        user = User.get_by_email('user@example.com')
        if user:
            if not Note.get_by_user(user.id):
                note1 = Note(
                    user_id=user.id,
                    content="Hoje refleti sobre a importância da fé em minha vida. Preciso confiar mais no plano divino.",
                    title="Reflexão sobre a fé",
                    is_favorite=True
                )
                note2 = Note(
                    user_id=user.id,
                    content="O versículo de hoje me lembrou que devo buscar a orientação divina em todas as minhas decisões.",
                    title="Buscando orientação"
                )
                db.session.add(note1)
                db.session.add(note2)
                print(f"Notas criadas para o usuário: {user.email}")
            else:
                print(f"Usuário {user.email} já possui notas")

        # Commit das alterações
        db.session.commit()
        print("População do banco de dados concluída com sucesso!")


if __name__ == '__main__':
    seed_database()
