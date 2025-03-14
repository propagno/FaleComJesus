#!/usr/bin/env python
"""
Master migration script that runs all migrations in the correct order.
"""
import sys
import os
import importlib
import time
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import migration modules
try:
    from migrations.add_prompt_templates import run_migration as run_add_prompt_templates
    from migrations.add_use_count_to_api_keys import run_migration as run_add_use_count_to_api_keys
except ImportError as e:
    print(f"Error importing migration module: {e}")
    sys.exit(1)


def run_migrations():
    """
    Run all migrations in sequence.
    """
    print("=" * 50)
    print(
        f"Starting migrations: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    migrations = [
        {
            "name": "Add Prompt Templates",
            "function": run_add_prompt_templates
        },
        {
            "name": "Add use_count to API Keys",
            "function": run_add_use_count_to_api_keys
        }
        # Add more migrations here as they are created
    ]

    for i, migration in enumerate(migrations, 1):
        print(
            f"\nRunning migration {i}/{len(migrations)}: {migration['name']}")
        print("-" * 50)

        start_time = time.time()

        try:
            migration["function"]()
            end_time = time.time()
            print(
                f"Migration completed successfully in {end_time - start_time:.2f} seconds")
        except Exception as e:
            print(f"Migration failed: {e}")
            print("Stopping migration process")
            sys.exit(1)

    print("\n" + "=" * 50)
    print("All migrations completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    run_migrations()
