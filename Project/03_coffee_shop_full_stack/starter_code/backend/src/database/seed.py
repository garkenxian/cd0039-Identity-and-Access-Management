"""
Database seeding script for Coffee Shop API.

This module provides functions to initialize and seed the SQLite database
with test data for development and testing environments.

Usage:
    python seed.py          # Initialize DB and seed with test data
    python seed.py --reset  # Reset DB completely (drop and recreate)
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from database.models import db, Drink, setup_db, db_drop_and_create_all


def create_app():
    """Create and configure Flask application for database operations."""
    app = Flask(__name__)
    setup_db(app)
    return app


def seed_drinks():
    """
    Seed the database with sample drink data.
    
    Adds a variety of coffee drinks with different recipes for testing
    different user permissions (barista, manager).
    """
    drinks = [
        {
            'title': 'Water',
            'recipe': [
                {'name': 'water', 'color': 'blue', 'parts': 1}
            ]
        },
        {
            'title': 'Coffee',
            'recipe': [
                {'name': 'espresso', 'color': 'brown', 'parts': 2},
                {'name': 'hot water', 'color': 'brown', 'parts': 3}
            ]
        },
        {
            'title': 'Tea',
            'recipe': [
                {'name': 'tea', 'color': 'brown', 'parts': 1},
                {'name': 'hot water', 'color': 'brown', 'parts': 2},
                {'name': 'lemon', 'color': 'yellow', 'parts': 1}
            ]
        },
        {
            'title': 'Cappuccino',
            'recipe': [
                {'name': 'espresso', 'color': 'brown', 'parts': 1},
                {'name': 'steamed milk', 'color': 'white', 'parts': 2},
                {'name': 'foam', 'color': 'white', 'parts': 1}
            ]
        },
        {
            'title': 'Latte',
            'recipe': [
                {'name': 'espresso', 'color': 'brown', 'parts': 1},
                {'name': 'steamed milk', 'color': 'white', 'parts': 3},
                {'name': 'foam', 'color': 'white', 'parts': 0.5}
            ]
        },
        {
            'title': 'Macchiato',
            'recipe': [
                {'name': 'espresso', 'color': 'brown', 'parts': 2},
                {'name': 'foam', 'color': 'white', 'parts': 1}
            ]
        },
        {
            'title': 'Mocha',
            'recipe': [
                {'name': 'espresso', 'color': 'brown', 'parts': 1},
                {'name': 'chocolate', 'color': 'brown', 'parts': 1},
                {'name': 'steamed milk', 'color': 'white', 'parts': 2}
            ]
        },
        {
            'title': 'Americano',
            'recipe': [
                {'name': 'espresso', 'color': 'brown', 'parts': 2},
                {'name': 'hot water', 'color': 'brown', 'parts': 2}
            ]
        }
    ]
    
    added = 0
    failed = 0
    
    for drink_data in drinks:
        try:
            drink = Drink(
                title=drink_data['title'],
                recipe=json.dumps(drink_data['recipe'])
            )
            drink.insert()
            print(f"✓ Added drink: {drink_data['title']}")
            added += 1
        except Exception as e:
            print(f"✗ Failed to add drink '{drink_data['title']}': {str(e)}")
            failed += 1
    
    return added, failed


def reset_database(app):
    """
    Completely reset the database (drop all tables and recreate).
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        print("Resetting database...")
        db_drop_and_create_all()
        print("✓ Database reset complete")
        return True


def initialize_database(app, seed=True):
    """
    Initialize the database with tables and optionally seed with data.
    
    Args:
        app: Flask application instance
        seed: If True, seed with sample data (default: True)
    
    Returns:
        tuple: (success, message)
    """
    with app.app_context():
        try:
            print("Initializing database...")
            db_drop_and_create_all()
            print("✓ Database tables created")
            
            if seed:
                print("\nSeeding database with sample data...")
                added, failed = seed_drinks()
                print(f"\n✓ Database seeding complete: {added} drinks added, {failed} failed")
                return True, f"Database initialized and seeded with {added} drinks"
            else:
                return True, "Database initialized (no seed data added)"
                
        except Exception as e:
            error_msg = f"Database initialization failed: {str(e)}"
            print(f"✗ {error_msg}")
            return False, error_msg


def main():
    """Main entry point for database seeding script."""
    app = create_app()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--reset':
            reset_database(app)
        elif sys.argv[1] == '--no-seed':
            initialize_database(app, seed=False)
        elif sys.argv[1] == '--help':
            print(__doc__)
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information")
            sys.exit(1)
    else:
        # Default: initialize and seed
        success, message = initialize_database(app, seed=True)
        if not success:
            sys.exit(1)


if __name__ == '__main__':
    main()
