from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models import BibleVerse, db
from app.schemas.bible_verse import BibleVerseSchema

bible_verses_bp = Blueprint(
    'bible_verses', __name__, url_prefix='/bible-verses')


@bible_verses_bp.route('/random', methods=['GET'])
@jwt_required()
def get_random_verse():
    """Get a random Bible verse"""
    limit = request.args.get('limit', 1, type=int)
    if limit > 10:
        limit = 10  # Cap at 10 to prevent abuse

    verses = BibleVerse.get_random(limit=limit)

    if not verses:
        return jsonify({'message': 'No Bible verses available'}), 404

    return jsonify(BibleVerseSchema(many=True).dump(verses)), 200


@bible_verses_bp.route('/search', methods=['GET'])
@jwt_required()
def search_verses():
    """Search Bible verses by text content"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)

    if not query:
        return jsonify({'message': 'Search query is required'}), 400

    if limit > 50:
        limit = 50  # Cap at 50 to prevent abuse

    verses = BibleVerse.search(query, limit=limit)

    return jsonify(BibleVerseSchema(many=True).dump(verses)), 200


@bible_verses_bp.route('/<string:book>/<int:chapter>/<int:verse>', methods=['GET'])
@jwt_required()
def get_verse_by_reference(book, chapter, verse):
    """Get a Bible verse by reference"""
    translation = request.args.get('translation', 'NVI')

    bible_verse = BibleVerse.get_by_reference(
        book, chapter, verse, translation)

    if not bible_verse:
        return jsonify({'message': 'Bible verse not found'}), 404

    return jsonify(BibleVerseSchema().dump(bible_verse)), 200

# Admin endpoints for managing Bible verses


@bible_verses_bp.route('', methods=['POST'])
@jwt_required()
def create_bible_verse():
    """Create a new Bible verse (admin only)"""
    # TODO: Add admin role check

    data = request.get_json()
    schema = BibleVerseSchema()

    try:
        # Validate and deserialize input
        bible_verse = schema.load(data)

        # Check if verse already exists
        existing = BibleVerse.get_by_reference(
            bible_verse.book,
            bible_verse.chapter,
            bible_verse.verse,
            bible_verse.translation
        )

        if existing:
            return jsonify({'message': 'Bible verse already exists'}), 409

        # Save the new verse
        bible_verse.save()

        return jsonify(schema.dump(bible_verse)), 201

    except Exception as e:
        return jsonify({'message': str(e)}), 400
