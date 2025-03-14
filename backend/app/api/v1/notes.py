from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Note, db
from app.schemas.note import NoteSchema
from datetime import date

notes_bp = Blueprint('notes', __name__, url_prefix='/notes')


@notes_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_notes():
    """Get the user's most recent notes (last 2)"""
    user_id = get_jwt_identity()
    notes = Note.get_recent_by_user(user_id, limit=2)

    return jsonify(NoteSchema(many=True).dump(notes)), 200


@notes_bp.route('', methods=['GET'])
@jwt_required()
def get_all_notes():
    """Get all notes for the current user"""
    user_id = get_jwt_identity()
    notes = Note.query.filter_by(
        user_id=user_id).order_by(Note.created_at.desc()).all()

    return jsonify(NoteSchema(many=True).dump(notes)), 200


@notes_bp.route('/<int:note_id>', methods=['GET'])
@jwt_required()
def get_note(note_id):
    """Get a specific note by ID"""
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()

    if not note:
        return jsonify({'message': 'Note not found'}), 404

    return jsonify(NoteSchema().dump(note)), 200


@notes_bp.route('', methods=['POST'])
@jwt_required()
def create_note():
    """Create a new note"""
    user_id = get_jwt_identity()
    data = request.get_json()

    # Add user_id to data
    data['user_id'] = user_id

    schema = NoteSchema()

    try:
        # Validate and deserialize input
        note = schema.load(data)

        # Save the new note
        note.save()

        return jsonify(schema.dump(note)), 201

    except Exception as e:
        return jsonify({'message': str(e)}), 400


@notes_bp.route('/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    """Update an existing note"""
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()

    if not note:
        return jsonify({'message': 'Note not found'}), 404

    data = request.get_json()

    # Add user_id to data to ensure ownership
    data['user_id'] = user_id

    schema = NoteSchema()

    try:
        # Update only the content field
        if 'content' in data:
            note.content = data['content']
            db.session.commit()

        return jsonify(schema.dump(note)), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400


@notes_bp.route('/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    """Delete a note"""
    user_id = get_jwt_identity()
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()

    if not note:
        return jsonify({'message': 'Note not found'}), 404

    try:
        note.delete()
        return jsonify({'message': 'Note deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400
