from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy instance
db = SQLAlchemy()


def init_db(app):
    """
    Initialize database with app context
    """
    db.init_app(app)
    with app.app_context():
        db.create_all()


def reset_db(app):
    """
    Reset database - FOR TESTING ONLY
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
