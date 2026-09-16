# Backend Test Coverage Documentation

## Overview
The backend test suite automatically generates comprehensive coverage reports to track code quality and testing completeness.

## Coverage Reports Generated

Every time tests run (`pytest`), the following reports are generated:

### 1. Terminal Report (Console Output)
- **Format**: Missing lines with line numbers shown in terminal
- **Location**: Printed to stdout during test execution
- **Shows**: Statements missed, branch coverage, total coverage percentage

Example output:
```
Name                       Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------------
src\api.py                   102     61     18      0    34%   41-42, 61-69, ...
src\auth\auth.py              74      7     20      0    93%   159-160, ...
----------------------------------------------------------------------
TOTAL                        222     73     38      0    65%
```

### 2. HTML Report
- **Location**: `htmlcov/index.html`
- **View**: Open in browser for interactive coverage analysis
- **Features**: 
  - Line-by-line coverage highlighting
  - Per-file and per-class coverage metrics
  - Drill-down into uncovered code paths

### 3. XML Report
- **Location**: `coverage.xml`
- **Purpose**: Integration with CI/CD tools (CodeCov, etc.)
- **Usage**: Automatically uploaded by GitHub Actions workflow

## Running Tests with Coverage

### Standard Test Execution
```bash
cd backend
pytest tests/
```

This automatically:
1. Runs all tests
2. Collects coverage data
3. Generates all three report formats
4. Displays summary in terminal

### View HTML Coverage Report
After running tests:
```bash
# Open in default browser (Windows)
start htmlcov/index.html

# Or manually open: backend/htmlcov/index.html in your browser
```

### Run Specific Test with Coverage
```bash
pytest tests/test_auth.py -v
pytest tests/test_endpoints.py -v
```

## Current Coverage Status

| Module | Coverage | Status |
|--------|----------|--------|
| auth/auth.py | 93% | ✅ Excellent |
| database/models.py | 89% | ✅ Very Good |
| api.py | 34% | ⏳ Pending Auth0 |
| **Total** | **65%** | ⏳ Pending full endpoint tests |

### Coverage Breakdown

**High Coverage Modules:**
- `auth/auth.py`: 93% - JWT parsing, verification, and permission checking fully tested
- `database/models.py`: 89% - CRUD operations and data model validation tested
- `__init__.py` files: 100% - Empty modules

**Lower Coverage Modules:**
- `api.py`: 34% - Endpoint handlers require Auth0 tokens for testing
  * `GET /drinks` (public): 100% tested
  * Secured endpoints: Auth decorator verified, full logic testable with Auth0

### Why 65% Total Instead of 80%?

Current test suite covers:
- ✅ All auth module functionality (JWT, permissions)
- ✅ All database model CRUD operations
- ✅ Public endpoints
- ⏳ Secured endpoint business logic (requires Auth0 tokens)

**Full 80%+ coverage will be achieved in Phase 3/4 when:**
1. Auth0 credentials are configured
2. Valid JWT tokens are generated for test users
3. Integration tests run with real authentication flow

## Configuration

### pytest.ini
Configures coverage options:
```ini
addopts = 
    --cov=src              # Coverage on src directory
    --cov-report=term-missing   # Terminal with missing lines
    --cov-report=html      # HTML interactive report
    --cov-report=xml       # XML for CI/CD integration
    --cov-branch           # Branch coverage analysis
    -v                     # Verbose test output
```

### .gitignore
Coverage artifacts are excluded from version control:
```
.coverage
htmlcov/
coverage.xml
```

## CI/CD Integration

GitHub Actions workflow (`.github/workflows/tests.yml`):
- Runs pytest with coverage on every push/PR
- Enforces `--cov-fail-under=80` for submission readiness
- Uploads coverage reports to CodeCov
- Archives HTML coverage as GitHub Actions artifact

## Coverage Targets

- **Auth Module**: 90%+ (security-critical)
- **Database Module**: 85%+ (data persistence)
- **API Endpoints**: 80%+ (after Auth0 integration)
- **Overall Backend**: 80%+ (required for submission)

## Improving Coverage

### Add More Tests
```bash
# Run tests with missing line report
pytest tests/ --cov-report=term-missing

# Open HTML report to identify untested paths
start htmlcov/index.html
```

### Test Secured Endpoints
Once Auth0 is configured:
1. Generate valid JWT tokens for test users
2. Add integration tests using real tokens
3. Coverage for secured endpoints will increase automatically

### Example: Testing Secured Endpoint
```python
# After Auth0 config
def test_post_drink_success(auth_token):
    """Test POST /drinks with valid token"""
    response = client.post(
        '/drinks',
        headers={'Authorization': f'Bearer {auth_token}'},
        json={'title': 'Latte', 'recipe': [...]}
    )
    assert response.status_code == 200
```

## Troubleshooting

### Coverage report not generating?
```bash
# Reinstall coverage dependencies
pip install pytest-cov --upgrade

# Verify pytest.ini is in backend directory
ls backend/pytest.ini

# Run with verbose output
pytest tests/ -vvv
```

### HTML report incomplete?
```bash
# Delete old coverage data and regenerate
rm .coverage htmlcov/coverage.xml
pytest tests/
start htmlcov/index.html
```

### Branch coverage gaps?
Coverage includes both line and branch coverage (decisions). This can show gaps in conditional logic not executed in current tests.

## Next Steps

1. **Phase 3**: Configure Auth0 and add integration tests
2. **Increase Endpoint Coverage**: Use real JWT tokens in tests
3. **Reach 80%+**: All modules >= 80% coverage
4. **Submit**: Include coverage report in project submission

## References

- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [GitHub Actions Coverage Integration](https://github.com/codecov/codecov-action)
