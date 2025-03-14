from flask import Blueprint, request, jsonify
from flask.views import MethodView
from marshmallow import Schema, fields, validate, ValidationError

from app.models.note import Note
from app.models.user import User
from app.utils.security import token_required
from app.utils.rate_limit import rate_limit

notes_bp = Blueprint('notes', __name__, url_prefix='/api/notes')


class NoteSchema(Schema):
    """Schema for note validation"""
    content = fields.String(required=True)
    title = fields.String(required=False, allow_none=True)
    is_favorite = fields.Boolean(required=False, default=False)


class NoteListSchema(Schema):
    """Schema for list of notes"""
    notes = fields.List(fields.Nested(NoteSchema))


class NoteResource(MethodView):
    """Notes API resource"""

    @token_required
    @rate_limit(limit=50, period=60, key_prefix='notes_list')
    def get(self, user_id):
        """Get notes for the authenticated user"""
        # Get query parameters
        limit = request.args.get('limit', None)
        favorite_only = request.args.get('favorite', 'false').lower() == 'true'

        if limit and limit.isdigit():
            limit = int(limit)
        else:
            limit = None

        # Get notes
        if favorite_only:
            notes = Note.get_favorites_by_user(user_id)
        else:
            notes = Note.get_by_user(user_id, limit)

        # Return notes
        return jsonify({
            'notes': [note.to_dict() for note in notes],
            'count': len(notes)
        }), 200

    @token_required
    @rate_limit(limit=20, period=60, key_prefix='notes_create')
    def post(self, user_id):
        """Create a new note for the authenticated user"""
        # Validate request data
        schema = NoteSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({'error': 'Validation error', 'details': err.messages}), 400

        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Create note
        note = Note(
            user_id=user_id,
            content=data['content'],
            title=data.get('title'),
            is_favorite=data.get('is_favorite', False)
        )
        note.save()

        # Return created note
        return jsonify({
            'message': 'Note created successfully',
            'note': note.to_dict()
        }), 201

    @token_required
    @rate_limit(limit=20, period=60, key_prefix='notes_update')
    def put(self, user_id, note_id):
        """Update a note for the authenticated user"""
        # Validate request data
        schema = NoteSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({'error': 'Validation error', 'details': err.messages}), 400

        # Get note
        note = Note.query.get(note_id)

        # Check if note exists and belongs to the user
        if not note or note.user_id != user_id:
            return jsonify({'error': 'Note not found'}), 404

        # Update note
        note.content = data['content']
        if 'title' in data:
            note.title = data['title']
        if 'is_favorite' in data:
            note.is_favorite = data['is_favorite']
        note.save()

        # Return updated note
        return jsonify({
            'message': 'Note updated successfully',
            'note': note.to_dict()
        }), 200

    @token_required
    @rate_limit(limit=20, period=60, key_prefix='notes_delete')
    def delete(self, user_id, note_id):
        """Delete a note for the authenticated user"""
        # Get note
        note = Note.query.get(note_id)

        # Check if note exists and belongs to the user
        if not note or note.user_id != user_id:
            return jsonify({'error': 'Note not found'}), 404

        # Delete note
        note.delete()

        # Return success
        return jsonify({
            'message': 'Note deleted successfully'
        }), 200


# Register the Notes resource
notes_view = NoteResource.as_view('notes_resource')
notes_bp.add_url_rule('', view_func=notes_view, methods=['GET', 'POST'])
notes_bp.add_url_rule(
    '/<int:note_id>', view_func=notes_view, methods=['PUT', 'DELETE'])
