"""
Pytest configuration and fixtures for backend tests
"""

import os
import sys

# Add backend directory to path so src can be imported as a package
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Set test environment
os.environ['FLASK_ENV'] = 'test'
os.environ['TESTING'] = 'true'

