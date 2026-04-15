# LinkDB Backend

FastAPI backend for LinkDB with SQLAlchemy ORM, Alembic migrations, and comprehensive test coverage.

## Requirements

- Python 3.13+
- MySQL 8+ (for local and production use)
- pip or pipenv

## Quick Start

### 1. Install Dependencies

```bash
python -m pip install -e .[dev]
```

The `[dev]` extra includes pytest and development tools.

### 2. Environment Setup

Copy the example environment file:

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

### 3. Start Database

Assuming you have MySQL running (via Docker Compose in `../infra`):

```bash
cd ../infra
docker compose up -d mysql
```

### 4. Run Migrations

```bash
alembic upgrade head
```

### 5. Start Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

The API will be available at `http://localhost:3000`.

---

## Configuration

All configuration is environment-based via `.env`:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | MySQL connection string | `mysql://user:pass@localhost:3306/linkdb` |
| `CORS_ORIGIN` | Allowed frontend origins (comma-separated) | `http://localhost:5173` |
| `AUTH_TOKEN_SECRET` | Secret for signing session tokens (32+ chars) | `your-secret-here` |
| `AUTH_COOKIE_NAME` | Session cookie name | `linkdb_session` |
| `AUTH_TOKEN_TTL_DAYS` | Session expiration in days | `7` |
| `LOGIN_RATE_LIMIT_WINDOW_MS` | Rate limit window in milliseconds | `900000` (15 min) |
| `LOGIN_RATE_LIMIT_MAX_REQUESTS` | Max login attempts per window | `10` |
| `JSON_BODY_LIMIT` | Max request body size | `100kb` |
| `PORT` | Server port | `3000` |
| `NODE_ENV` | Environment mode | `development` or `production` |

⚠️ **Critical:** `AUTH_TOKEN_SECRET` must be a strong, unique random string in production. Never use the placeholder value.

---

## Admin CLI Scripts

User and category management happens entirely through CLI (no public registration API):

```bash
# Create user (password is bcrypt-hashed)
python -m app.scripts.create_user [username] [password]

# Create category
python -m app.scripts.create_category [slug] [display-name]

# Reset user password
python -m app.scripts.reset_password [username] [new-password]

# Delete user
python -m app.scripts.delete_user [username]

# Seed demo users (useful for testing)
python -m app.scripts.seed_demo_users
```

### Examples

```bash
python -m app.scripts.create_user alice alice123
python -m app.scripts.create_category webdev "Web Development"
python -m app.scripts.reset_password alice newpassword456
```

---

## Testing

Run all tests with pytest:

```bash
python -m pytest
```

Run specific test file:

```bash
python -m pytest tests/test_auth_routes.py -v
```

Run with coverage:

```bash
python -m pytest --cov=app --cov-report=html
```

### Current Test Coverage

- ✅ Authentication routes (`/api/auth/login`, `/api/auth/logout`, `/api/auth/me`)
- ✅ Authentication service (password hashing, token creation)
- ✅ Links routes and service (CRUD operations)
- ✅ Category routes and service
- ✅ Read Later routes and service
- ✅ Session cookie flow and authentication
- ✅ Invalid JSON and validation error handling
- ✅ Rate limiting on login

---

## API Endpoints

### Authentication

```
POST   /api/auth/login      # username + password → session cookie
POST   /api/auth/logout     # Clear session
GET    /api/auth/me         # Current user info
```

### Links

```
GET    /api/links           # List user's links (paginated, filterable)
POST   /api/links           # Create new link
GET    /api/links/{id}      # Get single link
PATCH  /api/links/{id}      # Update link
DELETE /api/links/{id}      # Delete link
```

### Categories

```
GET    /api/categories      # List all categories
```

### Read Later

```
GET    /api/read-later              # Get user's read-later list
POST   /api/read-later/{linkId}     # Add link to read-later
DELETE /api/read-later/{linkId}     # Remove link from read-later
```

Each link in responses includes `isInReadLater: boolean` for the authenticated user.

---

## Database Migrations

Manage schema changes with Alembic:

```bash
# Apply latest migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Create new migration (auto-detect schema changes)
alembic revision --autogenerate -m "migration message"
```

All migrations are version-controlled in `alembic/versions/`.

---

## Project Structure

```
app/
├── main.py                # FastAPI app setup and lifecycle
├── api/
│   └── routes.py          # All route handlers
├── services/              # Business logic layer
│   ├── auth.py
│   ├── links.py
│   ├── categories.py
│   └── read_later.py
├── db/
│   ├── models.py          # SQLAlchemy ORM models
│   ├── session.py         # Database session management
│   └── category_seed.py   # Category data
├── dependencies/
│   └── auth.py            # Dependency injection for authenticated requests
├── security/
│   ├── password.py        # Bcrypt password hashing
│   └── session.py         # JWT-like token signing
├── schemas/               # Pydantic request/response models
├── core/
│   ├── config.py          # Settings from environment
│   ├── errors.py          # Custom exceptions
│   ├── http.py            # HTTP response utilities
│   └── rate_limit.py      # Rate limiting logic
└── scripts/               # Admin CLI tools

alembic/
├── env.py                 # Alembic configuration
└── versions/              # Migration files

tests/
├── conftest.py            # Pytest fixtures
├── test_auth_*.py
├── test_links_*.py
├── test_categories.py
└── test_read_later.py
```

---

## Development Notes

### Password Security

- Passwords are **never** stored in plain text
- All passwords are hashed with **bcrypt** (12 rounds) on creation
- Passwords cannot be retrieved, only reset

### Sessions

- Session tokens are **signed** with `AUTH_TOKEN_SECRET`
- Stored as **HttpOnly** cookies (immune to JavaScript access)
- TTL is configurable via `AUTH_TOKEN_TTL_DAYS`

### Rate Limiting

- Login attempts are rate-limited per IP
- Window: `LOGIN_RATE_LIMIT_WINDOW_MS` (default: 15 minutes)
- Max attempts: `LOGIN_RATE_LIMIT_MAX_REQUESTS` (default: 10)

### CORS

- Requires frontend origin in `CORS_ORIGIN` to access API
- Multiple origins supported (comma-separated)

---

## Docker

Production Docker image defined in [Dockerfile](Dockerfile):

1. Installs dependencies
2. Runs `alembic upgrade head` on startup
3. Serves API via Uvicorn on port 3000

Build locally:

```bash
docker build -t linkdb-backend .
docker run -p 3000:3000 --env-file .env linkdb-backend
```

---

## Troubleshooting

**"Can't connect to MySQL"**
- Verify `DATABASE_URL` in `.env`
- Check MySQL is running: `docker compose ps`
- Check credentials match `infra/.env`

**"AUTH_TOKEN_SECRET must be set"**
- Edit `.env` and set `AUTH_TOKEN_SECRET` to a random 32+ character string

**"Migration failed"**
- Check database is up: `docker compose logs mysql`
- Verify no stale connections: `alembic current`
- Check migration file syntax in `alembic/versions/`

---

## See Also

- [Main README](../README.md) for full project setup
- [Frontend README](../frontend/README.md) for React app
- [E2E Checklist](../docs/e2e-checklist.md) for deployment verification
