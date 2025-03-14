#!/usr/bin/env python
"""
Migration to add use_count column to api_keys table.
"""
from sqlalchemy import Column, Integer, text
from app import create_app, db
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_migration():
    """
    Add use_count column to api_keys table if it doesn't exist.
    """
    app = create_app()
    with app.app_context():
        # Check if column exists
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('api_keys')]

        if 'use_count' not in columns:
            print("Adding use_count column to api_keys table...")
            # Add the column
            with db.engine.connect() as conn:
                conn.execute(
                    text('ALTER TABLE api_keys ADD COLUMN use_count INTEGER DEFAULT 0'))
            print("Column added successfully!")
        else:
            print("Column use_count already exists in api_keys table.")


if __name__ == "__main__":
    run_migration()
