from .database import db, BaseModel


class BibleVerse(db.Model, BaseModel):
    """Bible verse model for storing and retrieving Bible verses"""
    __tablename__ = 'bible_verses'

    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.String(50), nullable=False, index=True)
    chapter = db.Column(db.Integer, nullable=False)
    verse = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    # Default: Nova Versão Internacional
    translation = db.Column(db.String(10), nullable=False, default='NVI')

    def __init__(self, book, chapter, verse, text, translation='NVI'):
        self.book = book
        self.chapter = chapter
        self.verse = verse
        self.text = text
        self.translation = translation

    def to_dict(self):
        """Convert Bible verse to dictionary for serialization"""
        return {
            'id': self.id,
            'book': self.book,
            'chapter': self.chapter,
            'verse': self.verse,
            'text': self.text,
            'translation': self.translation,
            'reference': f"{self.book} {self.chapter}:{self.verse}"
        }

    @classmethod
    def get_random(cls, limit=1):
        """Get a random Bible verse"""
        return cls.query.order_by(db.func.random()).limit(limit).all()

    @classmethod
    def get_by_reference(cls, book, chapter, verse, translation='NVI'):
        """Get a Bible verse by reference"""
        return cls.query.filter_by(
            book=book,
            chapter=chapter,
            verse=verse,
            translation=translation
        ).first()

    @classmethod
    def search(cls, query, limit=10):
        """Search Bible verses by text content"""
        search_term = f"%{query}%"
        return cls.query.filter(cls.text.ilike(search_term)).limit(limit).all()
