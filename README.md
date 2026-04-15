# LinkDB

LinkDB is a private web app for saving, searching and sharing links among friends. Users are never self-registered: they are created manually through backend admin CLI commands.

## Stack

- Backend: Python + FastAPI + SQLAlchemy + Alembic
- Frontend: React + Vite + TypeScript + Tailwind CSS
- Database: MySQL
- Packaging and deploy: Docker Compose + Nginx
- Backend tests: Pytest

## Project structure

```text
backend/
frontend/
infra/
docs/
```

## Key files

- `backend/app/main.py`
- `backend/app/api/routes.py`
- `backend/app/services/auth.py`
- `backend/app/services/links.py`
- `backend/app/services/read_later.py`
- `backend/app/db/models.py`
- `backend/alembic/versions/20260415193000_initial_python_backend.py`
- `backend/alembic/versions/20260415210000_add_read_later_links.py`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/SearchLinksPage.tsx`
- `frontend/src/pages/NewLinkPage.tsx`
- `frontend/src/pages/ReadLaterPage.tsx`
- `frontend/src/api/`
- `infra/docker-compose.yml`
- `frontend/nginx/default.conf`
- `docs/e2e-checklist.md`

## Local setup

### 1. Environment variables

Create local env files from the examples:

```bash
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env
copy infra\.env.example infra\.env
```

On Unix systems:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
cp infra/.env.example infra/.env
```

### 2. Start local MySQL

```bash
cd infra
docker compose up -d mysql
```

For local host development the compose file exposes MySQL on `localhost:3306`.

### 3. Install dependencies

Backend:

```bash
cd backend
python -m pip install -e .[dev]
```

Frontend:

```bash
cd frontend
npm install
```

### 4. Run migrations

With MySQL running:

```bash
cd backend
alembic upgrade head
```

### 5. Create users manually

Users are not created through the public API.

```bash
cd backend
python -m app.scripts.create_user [username] [password]
python -m app.scripts.create_category [slug] [display-name]
python -m app.scripts.delete_user [username]
python -m app.scripts.reset_password [username] [password]
python -m app.scripts.seed_demo_users
```

`users.password` always stores a `bcrypt` hash, never the clear-text password.
Categories are loaded from the backend catalog, so categories created via CLI become selectable in the UI after reload.

## Frontend sections

After login the frontend is split into three dedicated sections:

- `/links/search`: search, filters, edit/delete own links, add/remove read later
- `/links/new`: create a new link
- `/links/read-later`: personal read/watch later list for the current user

### 6. Start backend and frontend

Backend:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

Frontend:

```bash
cd frontend
npm run dev
```

Local URLs:

- frontend: `http://localhost:5173`
- backend: `http://localhost:3000`
- health API: `http://localhost:3000/api/health`

## Environment variables

### Backend local

File: `backend/.env`

```env
NODE_ENV=development
PORT=3000
DATABASE_URL=mysql://linkdb:change-me-db-password@localhost:3306/linkdb
CORS_ORIGIN=http://localhost,http://localhost:5173
JSON_BODY_LIMIT=100kb
LOGIN_RATE_LIMIT_WINDOW_MS=900000
LOGIN_RATE_LIMIT_MAX_REQUESTS=10
AUTH_TOKEN_SECRET=change-me-in-production
AUTH_COOKIE_NAME=linkdb_session
AUTH_TOKEN_TTL_DAYS=7
```

### Backend production

Base file: `backend/.env.production.example`

```env
NODE_ENV=production
PORT=3000
DATABASE_URL=mysql://linkdb:change-me-db-password@mysql:3306/linkdb
CORS_ORIGIN=https://your-domain.example
JSON_BODY_LIMIT=100kb
LOGIN_RATE_LIMIT_WINDOW_MS=900000
LOGIN_RATE_LIMIT_MAX_REQUESTS=10
AUTH_TOKEN_SECRET=change-me-with-a-long-random-secret
AUTH_COOKIE_NAME=linkdb_session
AUTH_TOKEN_TTL_DAYS=7
```

### Frontend local

File: `frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:3000
```

### Frontend production

Base file: `frontend/.env.production.example`

```env
VITE_API_BASE_URL=
```

When using the bundled Nginx proxy, the frontend already requests paths like `/api/auth/login`, so the production base URL must stay empty.

### Docker Compose / VPS

File: `infra/.env`

```env
MYSQL_ROOT_PASSWORD=change-me-root-password
MYSQL_DATABASE=linkdb
MYSQL_USER=linkdb
MYSQL_PASSWORD=change-me-db-password
CORS_ORIGIN=https://your-domain.example
JSON_BODY_LIMIT=100kb
LOGIN_RATE_LIMIT_WINDOW_MS=900000
LOGIN_RATE_LIMIT_MAX_REQUESTS=10
AUTH_TOKEN_SECRET=change-me-with-a-long-random-secret
AUTH_COOKIE_NAME=linkdb_session
AUTH_TOKEN_TTL_DAYS=7
FRONTEND_PORT=80
```

`backend/.env` and `infra/.env` must reference the same MySQL credentials.

## Docker Compose

Start the full stack:

```bash
cd infra
docker compose up -d --build
```

Stop it:

```bash
docker compose down
```

Services:

- `mysql`: persistent MySQL service, also exposed on `3306` for local host development
- `backend`: FastAPI app + Alembic migrations
- `frontend`: public Nginx container serving the frontend and proxying `/api` to the backend

## Deploy on a VPS

### 1. Prepare the server

- Install Docker Engine
- Install Docker Compose plugin
- Open at least port `80` on the firewall
- Clone the repository on the VPS

### 2. Configure

```bash
cd infra
cp .env.example .env
```

Update at least:

- `MYSQL_ROOT_PASSWORD`
- `MYSQL_PASSWORD`
- `AUTH_TOKEN_SECRET`
- `CORS_ORIGIN`

### 3. Build and start

```bash
docker compose up -d --build
```

### 4. Migrations

The backend container applies Alembic migrations automatically on startup with `alembic upgrade head`.

### 5. Create the first user

```bash
docker compose exec backend python -m app.scripts.create_user [username] [password]
```

### 6. Initial checks

- `http://YOUR_DOMAIN_OR_IP/` reaches the frontend
- `http://YOUR_DOMAIN_OR_IP/api/health` responds
- frontend login works

## Backup and restore

### Backup MySQL

```bash
cd infra
docker compose exec mysql sh -c 'mysqldump -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' > backup.sql
```

### Restore MySQL

```bash
cd infra
Get-Content backup.sql | docker compose exec -T mysql sh -c 'mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"'
```

On Unix systems:

```bash
cd infra
cat backup.sql | docker compose exec -T mysql sh -c 'mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"'
```

## Tests

Backend:

```bash
cd backend
python -m pytest
```

Checklist end-to-end:

- `docs/e2e-checklist.md`

Backend verification currently covers:

- automated pytest coverage for auth service/routes and links service/routes
- automated pytest coverage for category catalog and read later flows
- invalid JSON handling and validation failures
- session cookie flow and authenticated CRUD
- manual smoke checks for Alembic migrations and admin CLI commands

## Current limitations

- no public user registration API
- no advanced roles or permissions
- simple signed session cookie with HttpOnly flag
- no full browser E2E suite
- deploy assumes HTTP unless TLS is terminated in front of Nginx
