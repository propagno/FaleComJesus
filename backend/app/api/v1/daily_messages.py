from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models import DailyMessage, db
from app.schemas.daily_message import DailyMessageSchema
from datetime import date

daily_messages_bp = Blueprint(
    'daily_messages', __name__, url_prefix='/daily-messages')


@daily_messages_bp.route('/today', methods=['GET'])
@jwt_required()
def get_today_message():
    """Get today's daily message"""
    message = DailyMessage.get_today()

    if not message:
        return jsonify({'message': 'No daily message available for today'}), 404

    return jsonify(DailyMessageSchema().dump(message)), 200


@daily_messages_bp.route('/<string:date_str>', methods=['GET'])
@jwt_required()
def get_message_by_date(date_str):
    """Get daily message for a specific date"""
    try:
        # Parse date string (format: YYYY-MM-DD)
        date_obj = date.fromisoformat(date_str)
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

    message = DailyMessage.get_by_date(date_obj)

    if not message:
        return jsonify({'message': f'No daily message available for {date_str}'}), 404

    return jsonify(DailyMessageSchema().dump(message)), 200

# Admin endpoints for managing daily messages


@daily_messages_bp.route('', methods=['POST'])
@jwt_required()
def create_daily_message():
    """Create a new daily message (admin only)"""
    # TODO: Add admin role check

    data = request.get_json()
    schema = DailyMessageSchema()

    try:
        # Validate and deserialize input
        daily_message = schema.load(data)

        # Check if a message already exists for this date
        existing = DailyMessage.get_by_date(daily_message.date)
        if existing:
            return jsonify({'message': f'A daily message already exists for {daily_message.date}'}), 409

        # Save the new message
        daily_message.save()

        return jsonify(schema.dump(daily_message)), 201

    except Exception as e:
        return jsonify({'message': str(e)}), 400
