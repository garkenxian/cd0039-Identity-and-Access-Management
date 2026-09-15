.PHONY: help install install-backend install-frontend \
	run run-backend run-frontend \
	test test-backend test-backend-coverage test-frontend \
	auth0-init auth0-init-help clean clean-backend clean-frontend \
	lint lint-backend lint-frontend format format-backend format-frontend setup

SHELL := cmd.exe
.SHELLFLAGS := /C
.SILENT:

# Directories (Windows-compatible)
BACKEND_DIR := Project\03_coffee_shop_full_stack\starter_code\backend
FRONTEND_DIR := Project\03_coffee_shop_full_stack\starter_code\frontend
HELPERS_DIR := $(BACKEND_DIR)\_helpers

# Python
PYTHON := python
VENV := venv
FLASK_APP := src/api.py

# Node
NODE_OPTIONS := --openssl-legacy-provider

help: ## Show this help message
	echo Coffee Shop Project - Make Commands
	echo SETUP
	echo   install                    Install all dependencies
	echo   install-backend            Install backend dependencies
	echo   install-frontend           Install frontend dependencies
	echo RUN
	echo   run                        Show commands to run backend/frontend
	echo   run-backend                Run Flask backend
	echo   run-frontend               Run Ionic frontend
	echo TEST
	echo   test                       Run backend + frontend tests
	echo   test-backend               Run backend tests
	echo   test-backend-coverage      Run backend tests with coverage
	echo   test-frontend              Run frontend tests
	echo LINT/FORMAT
	echo   lint                       Run backend + frontend lint
	echo   format                     Run backend + frontend formatting
	echo AUTH0
	echo   auth0-init-help            Show Auth0 setup instructions
	echo   auth0-init                 Initialize Auth0 resources
	echo CLEAN
	echo   clean                      Remove generated backend/frontend files

install: install-backend install-frontend ## Install all dependencies (backend + frontend)

install-backend: ## Install backend dependencies
	echo [Backend] Installing Python dependencies...
	cd /d "$(BACKEND_DIR)" && if not exist "$(VENV)\Scripts\python.exe" (echo Creating virtual environment... && $(PYTHON) -m venv "$(VENV)")
	cd /d "$(BACKEND_DIR)" && "$(VENV)\Scripts\python.exe" -m pip install --upgrade pip
	cd /d "$(BACKEND_DIR)" && "$(VENV)\Scripts\python.exe" -m pip install -r requirements.txt
	echo Backend dependencies installed

install-frontend: ## Install frontend dependencies
	echo [Frontend] Installing Node dependencies...
	cd /d "$(FRONTEND_DIR)" && npm install
	echo Frontend dependencies installed

run: ## Run both backend and frontend (in separate terminals)
	echo Starting Coffee Shop application...
	echo Tip: Use 'make run-backend' and 'make run-frontend' to run in separate terminals
	echo Backend: http://127.0.0.1:5000
	echo Frontend: http://localhost:8100
	echo Run these commands in separate terminals:
	echo   make run-backend
	echo   make run-frontend

run-backend: ## Run Flask backend (port 5000)
	echo [Backend] Starting Flask server...
	cd /d "$(BACKEND_DIR)" && set FLASK_APP=$(FLASK_APP) && set FLASK_ENV=development && "$(VENV)\Scripts\python.exe" -m flask run --reload

run-frontend: ## Run Ionic frontend (port 8100)
	echo [Frontend] Starting Ionic development server...
	cd /d "$(FRONTEND_DIR)" && set NODE_OPTIONS=$(NODE_OPTIONS) && ionic serve

test: test-backend test-frontend ## Run all tests (backend + frontend)

test-coverage: test-backend-coverage test-frontend

test-backend: ## Run backend unit tests
	echo [Backend] Running pytest tests...
	cd /d "$(BACKEND_DIR)" && "$(VENV)\Scripts\python.exe" -m pytest tests/ --tb=short

test-backend-coverage: ## Run backend tests with coverage report
	echo [Backend] Installing coverage dependencies...
	cd /d "$(BACKEND_DIR)" && "$(VENV)\Scripts\python.exe" -m pip install -q pytest-cov
	echo [Backend] Running pytest with coverage (minimum 80% required)...
	cd /d "$(BACKEND_DIR)" && "$(VENV)\Scripts\python.exe" -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=80
	echo Coverage report created in: htmlcov/index.html

test-frontend: ## Run frontend tests (Karma)
	echo [Frontend] Running Karma tests...
	cd /d "$(FRONTEND_DIR)" && cmd /C "set NODE_OPTIONS=$(NODE_OPTIONS) && npm test -- --watch=false --browsers=ChromeHeadless"
	echo Frontend tests passed

test-frontend-converage: test-frontend ## will put coverage report here when its ready

lint: lint-backend lint-frontend ## Run linters (backend + frontend)

lint-backend: ## Run pylint on backend code
	echo [Backend] Running pylint...
	cd /d "$(BACKEND_DIR)" && "$(VENV)\Scripts\python.exe" -m pylint src\ || echo Backend lint reported issues

lint-frontend: ## Run ESLint on frontend code
	echo [Frontend] Running ESLint...
	cd /d "$(FRONTEND_DIR)" && npm run lint || echo Frontend lint reported issues

format: format-backend format-frontend ## Format code (backend + frontend)

format-backend: ## Format backend code with isort
	echo [Backend] Formatting Python code...
	cd /d "$(BACKEND_DIR)" && "$(VENV)\Scripts\python.exe" -m isort src\ tests\
	echo Backend code formatted

format-frontend: ## Format frontend code
	echo [Frontend] Formatting TypeScript code...
	cd /d "$(FRONTEND_DIR)" && npm run format
	echo Frontend code formatted

auth0-init: ## Initialize Auth0 tenant (requires credentials)
	echo [Auth0] Setting up Auth0 configuration...
	if "$(AUTH0_DOMAIN)"=="" (echo AUTH0_DOMAIN is required. && exit /b 1)
	if "$(AUTH0_CLIENT_ID)"=="" (echo AUTH0_CLIENT_ID is required. && exit /b 1)
	if "$(AUTH0_CLIENT_SECRET)"=="" (echo AUTH0_CLIENT_SECRET is required. && exit /b 1)
	cd /d "$(HELPERS_DIR)" && $(PYTHON) auth0_setup.py --domain "$(AUTH0_DOMAIN)" --client-id "$(AUTH0_CLIENT_ID)" --client-secret "$(AUTH0_CLIENT_SECRET)"
	cd /d "$(HELPERS_DIR)" && if exist ".env" (copy /Y ".env" "..\\.env" >nul && echo Auth0 setup complete. .env copied to starter_code root.) else (echo Auth0 setup finished, but _helpers/.env was not found.)
	echo Manual step: enable 'Add Permissions in Access Token' in Auth0 API settings.

auth0-init-help: ## Show Auth0 setup help
	echo Auth0 Setup Instructions
	echo Step 1: Create Auth0 Account ^& Tenant
	echo Step 2: Create Management API Credentials
	echo Step 3: Run command:
	echo   make auth0-init AUTH0_DOMAIN=your-domain.auth0.com AUTH0_CLIENT_ID=your_client_id AUTH0_CLIENT_SECRET=your_client_secret
	echo Step 4: Enable 'Add Permissions in Access Token' in Auth0 API settings

clean: clean-backend clean-frontend ## Clean up all generated files

clean-backend: ## Clean backend virtual environment and cache
	echo [Backend] Cleaning...
	cd /d "$(BACKEND_DIR)" && if exist "$(VENV)" rmdir /S /Q "$(VENV)"
	powershell -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "Set-Location '$(BACKEND_DIR)'; Get-ChildItem -Recurse -Directory -Filter '__pycache__' -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue; Get-ChildItem -Recurse -File -Filter '*.pyc' -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue"
	echo Backend cleaned

clean-frontend: ## Clean frontend node_modules
	echo [Frontend] Cleaning...
	cd /d "$(FRONTEND_DIR)" && if exist "node_modules" rmdir /S /Q "node_modules"
	cd /d "$(FRONTEND_DIR)" && if exist "dist" rmdir /S /Q "dist"
	cd /d "$(FRONTEND_DIR)" && if exist "www" rmdir /S /Q "www"
	echo Frontend cleaned

setup: install ## Full project setup (alias for install)
	echo Project setup complete.
	echo Next steps:
	echo   1. Configure Auth0: make auth0-init-help
	echo   2. Run backend: make run-backend
	echo   3. Run frontend: make run-frontend
	echo   4. Run tests: make test

.DEFAULT_GOAL := help
