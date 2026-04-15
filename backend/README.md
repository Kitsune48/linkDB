# LinkDB Backend

Python backend for LinkDB built with FastAPI, SQLAlchemy and Alembic.

## Requirements

- Python 3.13+
- MySQL for normal local development

## Local setup

1. Install dependencies:
   `python -m pip install -e .[dev]`
2. Copy env file:
   `copy .env.example .env`
   On Unix: `cp .env.example .env`
3. Start MySQL:
   `cd ..\\infra && docker compose up -d mysql`
4. Apply migrations:
   `cd ..\\backend && alembic upgrade head`
5. Run the API:
   `uvicorn app.main:app --reload --host 0.0.0.0 --port 3000`

## Environment

Important variables:

- `DATABASE_URL`
- `CORS_ORIGIN`
- `AUTH_TOKEN_SECRET`
- `AUTH_COOKIE_NAME`
- `AUTH_TOKEN_TTL_DAYS`
- `LOGIN_RATE_LIMIT_WINDOW_MS`
- `LOGIN_RATE_LIMIT_MAX_REQUESTS`

`AUTH_TOKEN_SECRET` must be set for auth to work. In production it must not stay on the placeholder value.
`DATABASE_URL` should point to MySQL in normal local/deploy usage. SQLite is only useful for isolated smoke tests.
For local development with `infra/docker-compose.yml`, the password embedded in `DATABASE_URL` must match `MYSQL_PASSWORD` from `infra/.env`.
If you use the Docker frontend on `http://localhost`, include that origin in `CORS_ORIGIN`. If you use Vite dev server, also include `http://localhost:5173`.

## Admin CLI

- `python -m app.scripts.create_user <username> <password>`
- `python -m app.scripts.create_category <slug> <label>`
- `python -m app.scripts.delete_user <username>`
- `python -m app.scripts.reset_password <username> <new-password>`
- `python -m app.scripts.seed_demo_users`

## Tests

Run:

`python -m pytest`

Current automated coverage includes auth service/routes, links service/routes, session cookie flow, invalid JSON handling and CRUD behavior.
Manual smoke checks were also used for Alembic migrations and the admin CLI scripts.

## Read Later feature

The backend exposes per-user read later endpoints:

- `GET /api/read-later`
- `POST /api/read-later/:linkId`
- `DELETE /api/read-later/:linkId`

`GET /api/links` also returns `isInReadLater` on each link for the authenticated user.

## Docker

The production container defined in [Dockerfile](/C:/Users/gigi/Desktop/linkDB/backend/Dockerfile) installs the Python package, runs `alembic upgrade head` on startup and then serves the API with Uvicorn on port `3000`.
