.PHONY: help install install-backend install-frontend \
        run run-backend run-frontend \
        test test-backend test-frontend \
        auth0-init clean clean-backend clean-frontend \
        lint format

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

# Directories (Windows-compatible)
BACKEND_DIR := Project/03_coffee_shop_full_stack/starter_code/backend
FRONTEND_DIR := Project/03_coffee_shop_full_stack/starter_code/frontend
HELPERS_DIR := $(BACKEND_DIR)/_helpers

# Python
PYTHON := python3
VENV := $(BACKEND_DIR)/venv
FLASK_APP := src/api.py

# Node
NODE_OPTIONS := --openssl-legacy-provider

help: ## Show this help message
	@echo "$(BLUE)Coffee Shop Project - Make Commands$(NC)"
	@echo ""
	@echo "$(GREEN)SETUP$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'

install: install-backend install-frontend ## Install all dependencies (backend + frontend)

install-backend: ## Install backend dependencies
	@echo "$(GREEN)[Backend] Installing Python dependencies...$(NC)"
	@cd $(BACKEND_DIR) && \
	if [ ! -d $(VENV) ]; then \
		echo "$(BLUE)Creating virtual environment...$(NC)"; \
		$(PYTHON) -m venv venv; \
	fi && \
	. venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt && \
	echo "$(GREEN)✓ Backend dependencies installed$(NC)"

install-frontend: ## Install frontend dependencies
	@echo "$(GREEN)[Frontend] Installing Node dependencies...$(NC)"
	@cd $(FRONTEND_DIR) && \
	npm install && \
	echo "$(GREEN)✓ Frontend dependencies installed$(NC)"

run: ## Run both backend and frontend (in separate terminals)
	@echo "$(GREEN)Starting Coffee Shop application...$(NC)"
	@echo "$(BLUE)Tip: Use 'make run-backend' and 'make run-frontend' to run in separate terminals$(NC)"
	@echo ""
	@echo "$(GREEN)Starting backend on http://127.0.0.1:5000$(NC)"
	@echo "$(GREEN)Starting frontend on http://localhost:8100$(NC)"
	@echo ""
	@echo "Run these commands in separate terminals:"
	@echo "  $(BLUE)make run-backend$(NC)"
	@echo "  $(BLUE)make run-frontend$(NC)"

run-backend: ## Run Flask backend (port 5000)
	@echo "$(GREEN)[Backend] Starting Flask server...$(NC)"
	@cd $(BACKEND_DIR) && \
	. venv/bin/activate && \
	export FLASK_APP=$(FLASK_APP) && \
	export FLASK_ENV=development && \
	flask run --reload

run-frontend: ## Run Ionic frontend (port 8100)
	@echo "$(GREEN)[Frontend] Starting Ionic development server...$(NC)"
	@cd $(FRONTEND_DIR) && \
	export NODE_OPTIONS=$(NODE_OPTIONS) && \
	ionic serve

test: test-backend test-frontend ## Run all tests (backend + frontend)

test-backend: ## Run backend unit tests
	@echo "$(GREEN)[Backend] Running pytest tests...$(NC)"
	@cd $(BACKEND_DIR) && \
	. venv/bin/activate && \
	pytest tests/ -v --tb=short && \
	echo "$(GREEN)✓ Backend tests passed$(NC)"

test-backend-coverage: ## Run backend tests with coverage report
	@echo "$(GREEN)[Backend] Running pytest with coverage...$(NC)"
	@cd $(BACKEND_DIR) && \
	. venv/bin/activate && \
	pytest tests/ -v --cov=src --cov-report=html && \
	echo "$(GREEN)✓ Coverage report generated in htmlcov/index.html$(NC)"

test-frontend: ## Run frontend tests (Karma)
	@echo "$(GREEN)[Frontend] Running Karma tests...$(NC)"
	@cd $(FRONTEND_DIR) && \
	npm test -- --watch=false --browsers=ChromeHeadless && \
	echo "$(GREEN)✓ Frontend tests passed$(NC)"

lint: lint-backend lint-frontend ## Run linters (backend + frontend)

lint-backend: ## Run pylint on backend code
	@echo "$(GREEN)[Backend] Running pylint...$(NC)"
	@cd $(BACKEND_DIR) && \
	. venv/bin/activate && \
	pylint src/ || true

lint-frontend: ## Run ESLint on frontend code
	@echo "$(GREEN)[Frontend] Running ESLint...$(NC)"
	@cd $(FRONTEND_DIR) && \
	npm run lint || true

format: format-backend format-frontend ## Format code (backend + frontend)

format-backend: ## Format backend code with isort
	@echo "$(GREEN)[Backend] Formatting Python code...$(NC)"
	@cd $(BACKEND_DIR) && \
	. venv/bin/activate && \
	isort src/ tests/ && \
	echo "$(GREEN)✓ Backend code formatted$(NC)"

format-frontend: ## Format frontend code
	@echo "$(GREEN)[Frontend] Formatting TypeScript code...$(NC)"
	@cd $(FRONTEND_DIR) && \
	npm run format && \
	echo "$(GREEN)✓ Frontend code formatted$(NC)"

auth0-init: ## Initialize Auth0 tenant (requires credentials)
	@echo "$(GREEN)[Auth0] Setting up Auth0 configuration...$(NC)"
	@echo ""
	@echo "$(BLUE)Prerequisites:$(NC)"
	@echo "  1. Auth0 account created at auth0.com"
	@echo "  2. Tenant created (get domain: xxxxx.auth0.com)"
	@echo "  3. Management API credentials obtained:"
	@echo "     - Go to Applications > Applications > Create Application"
	@echo "     - Name: Coffee Shop Setup Bot"
	@echo "     - Type: Machine to Machine"
	@echo "     - In API dropdown, select 'Auth0 Management API'"
	@echo "     - Authorize all required scopes"
	@echo "     - Copy Client ID and Client Secret"
	@echo ""
	@echo "$(BLUE)Running setup script...$(NC)"
	@cd $(HELPERS_DIR) && $(PYTHON) auth0_setup.py --domain $(AUTH0_DOMAIN) --client-id $(AUTH0_CLIENT_ID) --client-secret $(AUTH0_CLIENT_SECRET)
	@copy "$(HELPERS_DIR)\.env" ".env" >nul 2>&1 || echo "Note: .env file should be in project root"
	@echo ""
	@echo "$(GREEN)✓ Auth0 setup complete!$(NC)"
	@echo "$(BLUE).env file created in $(HELPERS_DIR)$(NC)"
	@echo ""
	@echo "$(BLUE)Manual Step Required:$(NC)"
	@echo "  1. Go to Auth0 Dashboard"
	@echo "  2. Applications > APIs > Coffee Shop API > Settings"
	@echo "  3. Toggle ON: 'Add Permissions in Access Token'"
	@echo "  4. Save"
	@echo ""

auth0-init-help: ## Show Auth0 setup help
	@echo "$(BLUE)Auth0 Setup Instructions$(NC)"
	@echo ""
	@echo "Step 1: Create Auth0 Account & Tenant (5 min)"
	@echo "  - Go to https://auth0.com and create account"
	@echo "  - Create new tenant (e.g., coffee-shop-dev)"
	@echo "  - Note your domain: xxxxx.auth0.com"
	@echo ""
	@echo "Step 2: Create Management API Credentials (3 min)"
	@echo "  - Auth0 Dashboard > Applications > Applications > Create"
	@echo "  - Name: Coffee Shop Setup Bot"
	@echo "  - Type: Machine to Machine"
	@echo "  - In API dropdown: Auth0 Management API"
	@echo "  - Authorize all scopes"
	@echo "  - Copy Client ID and Client Secret"
	@echo ""
	@echo "Step 3: Run Setup Script (1 min)"
	@echo "  - make auth0-init AUTH0_DOMAIN=your-domain.auth0.com \\"
	@echo "              AUTH0_CLIENT_ID=your_client_id \\"
	@echo "              AUTH0_CLIENT_SECRET=your_client_secret"
	@echo ""
	@echo "Step 4: Enable RBAC Claims (1 min)"
	@echo "  - Auth0 Dashboard > APIs > Coffee Shop API > Settings"
	@echo "  - Toggle ON: 'Add Permissions in Access Token'"
	@echo "  - Save"
	@echo ""
	@echo "Done! Your .env file is ready."
	@echo ""

clean: clean-backend clean-frontend ## Clean up all generated files

clean-backend: ## Clean backend virtual environment and cache
	@echo "$(RED)[Backend] Cleaning...$(NC)"
	@cd $(BACKEND_DIR) && \
	rm -rf venv && \
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
	find . -type f -name "*.pyc" -delete && \
	echo "$(GREEN)✓ Backend cleaned$(NC)"

clean-frontend: ## Clean frontend node_modules
	@echo "$(RED)[Frontend] Cleaning...$(NC)"
	@cd $(FRONTEND_DIR) && \
	rm -rf node_modules dist www && \
	echo "$(GREEN)✓ Frontend cleaned$(NC)"

setup: install ## Full project setup (alias for install)
	@echo ""
	@echo "$(GREEN)✓ Project setup complete!$(NC)"
	@echo ""
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  1. Configure Auth0: make auth0-init-help"
	@echo "  2. Run backend: make run-backend"
	@echo "  3. Run frontend: make run-frontend (in another terminal)"
	@echo "  4. Run tests: make test"
	@echo ""

.DEFAULT_GOAL := help
