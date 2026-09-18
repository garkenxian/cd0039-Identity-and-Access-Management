# Database Seeding

This directory contains the database model, initialization, and seeding scripts for the Coffee Shop API.

## Files

- `models.py` - SQLAlchemy models for the Drink entity
- `seed.py` - Database initialization and seeding script
- `__init__.py` - Package initialization

## Database Schema

### Drink Model

| Field | Type | Details |
|-------|------|---------|
| `id` | Integer | Primary key, auto-incremented |
| `title` | String(80) | Drink name, must be unique |
| `recipe` | String(180) | JSON array of ingredients |

Recipe format:
```json
[
  {
    "name": "ingredient name",
    "color": "color code or name",
    "parts": 1.5
  }
]
```

## Quick Start

### Initialize Database with Test Data

```bash
# Using make
make db-init

# Or directly with Python
cd backend
python src/database/seed.py
```

This will:
1. Drop existing tables
2. Create fresh tables
3. Seed with 8 sample drinks (Water, Coffee, Tea, Cappuccino, Latte, Macchiato, Mocha, Americano)

### Reset Database Completely

```bash
# Using make
make db-reset

# Or directly
python src/database/seed.py --reset
```

Drops all tables and creates empty ones (with just the initial "water" drink from `db_drop_and_create_all()`).

### Seed Without Reset

```bash
# Using make
make db-seed

# Or directly  
python src/database/seed.py --no-seed
```

Reinitializes tables without dropping (useful for clearing duplicates).

## Usage in Code

### Import and use in Flask app

```python
from src.database.models import setup_db, db_drop_and_create_all
from src.database.seed import initialize_database

app = Flask(__name__)
setup_db(app)

with app.app_context():
    # Initialize database
    success, message = initialize_database(app, seed=True)
    if success:
        print(message)
```

## Sample Data

The seed file includes 8 drinks:

1. **Water** - Simple water drink
2. **Coffee** - Espresso with hot water
3. **Tea** - Tea with hot water and lemon
4. **Cappuccino** - Espresso with steamed milk and foam
5. **Latte** - Espresso with steamed milk
6. **Macchiato** - Espresso with foam
7. **Mocha** - Espresso with chocolate and steamed milk
8. **Americano** - Espresso with hot water

Each drink is added to test different CRUD operations and permission levels (Barista can view, Manager can create/edit/delete).

## Development Workflow

1. **First time setup**:
   ```bash
   make install-backend
   make db-init
   make run-backend
   ```

2. **Reset database during testing**:
   ```bash
   make db-reset
   ```

3. **Add to database while running**:
   ```
   Use Postman or curl to POST to /drinks endpoint
   ```

## Database File Location

The SQLite database is created at:
```
backend/src/database/database.db
```

This file is ignored by git (in `.gitignore`) to prevent committing local test state.
