@echo off
REM View coverage report - run after pytest

REM Check if coverage report exists
if not exist "htmlcov\index.html" (
    echo Coverage report not found. Running tests first...
    pytest tests/
)

REM Open report in default browser
start htmlcov\index.html

echo.
echo Coverage report opened in browser.
echo Report location: %cd%\htmlcov\index.html
