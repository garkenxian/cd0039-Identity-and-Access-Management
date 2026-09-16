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


def pytest_configure(config):
    """
    Configure pytest with coverage options if pytest-cov is available.
    This allows users to optionally get coverage reports without requiring
    all tests to include coverage overhead.
    """
    try:
        import pytest_cov
        # If pytest-cov is available, you can enable coverage here if desired
        # Otherwise, users can run: pytest tests/ --cov=src --cov-report=html
        pass
    except ImportError:
        pass


