#!/bin/bash
# View coverage report - run after pytest

# Check if coverage report exists
if [ ! -f "htmlcov/index.html" ]; then
    echo "Coverage report not found. Running tests first..."
    pytest tests/
fi

# Determine OS and open report
if command -v open &> /dev/null; then
    # macOS
    open htmlcov/index.html
elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open htmlcov/index.html
elif command -v start &> /dev/null; then
    # Windows (Git Bash)
    start htmlcov/index.html
else
    echo "Coverage HTML report location: $(pwd)/htmlcov/index.html"
    echo "Open this file in your web browser to view the coverage report."
fi
