# LinkDB

> A private web app for saving, searching, and sharing links among friends.

Users are created exclusively through backend admin CLI commands—no self-registration.

## Features

- 🔐 Session-based authentication with secure HTTP-only cookies
- 🔗 Save, organize, and search links with category tagging
- 📚 Personal "Read Later" list per user
- 🚀 Fast, type-safe stack with Python and TypeScript
- 🐳 Production-ready Docker Compose setup
- ✅ Comprehensive automated tests

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.13, FastAPI, SQLAlchemy, Alembic |
| **Frontend** | React 18+, Vite, TypeScript, Tailwind CSS |
| **Database** | MySQL 8+ |
| **Deployment** | Docker Compose, Nginx |
| **Testing** | Pytest |

## Project Structure

```
linkdb/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py              # Entry point
│   │   ├── api/routes.py         # API endpoints
│   │   ├── services/             # Business logic
│   │   ├── db/models.py          # SQLAlchemy models
│   │   └── scripts/              # Admin CLI tools
│   └── alembic/                  # Database migrations
├── frontend/             # React application
│   └── src/
│       ├── pages/                # Page components
│       ├── components/           # Reusable components
│       └── api/                  # API client
├── infra/                # Docker Compose configuration
└── docs/                 # Documentation

## Quick Start

### Prerequisites

- **Backend**: Python 3.13+, pip
- **Frontend**: Node.js 18+, npm
- **Database**: Docker + Docker Compose (for local MySQL)

### 1. Clone & Setup Environment

```bash
git clone https://github.com/Kitsune48/linkDB.git
cd linkdb
```

Create `.env` files from templates:

**Windows:**
```powershell
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env
copy infra\.env.example infra\.env
```

**Mac/Linux:**
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
cp infra/.env.example infra/.env
```

### 2. Start MySQL

```bash
cd infra
docker compose up -d mysql
```

MySQL will be available at `localhost:3306`.

### 3. Backend Setup

```bash
cd backend
python -m pip install -e .[dev]
alembic upgrade head
```

### 4. Frontend Setup

```bash
cd frontend
npm install
```

### 5. Run Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### 6. Create Your First User

```bash
cd backend
python -m app.scripts.create_user [username] [password]
```

Example:
```bash
python -m app.scripts.create_user alice alice123
```

**Note:** Passwords are bcrypt-hashed immediately, never stored in plain text.

---

## User Management (CLI)

```bash
# Create user
python -m app.scripts.create_user [username] [password]

# Create category  
python -m app.scripts.create_category [slug] [display-name]

# Reset password
python -m app.scripts.reset_password [username] [password]

# Delete user
python -m app.scripts.delete_user [username]

# Seed demo users
python -m app.scripts.seed_demo_users
```

---

## Frontend Sections

Once logged in, the app has three main sections:

| Path | Purpose |
|------|---------|
| `/links/search` | Search, filter, and manage your links; add/remove items from read later |
| `/links/new` | Create and submit new links |
| `/links/read-later` | View your personal read/watch later list |

---

## API Health Check

```bash
curl http://localhost:3000/api/health
```

---

## Environment Variables

### Backend (backend/.env)

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

### Frontend (frontend/.env)

```env
VITE_API_BASE_URL=http://localhost:3000
```

### Docker Compose (infra/.env)

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

**Important:** `backend/.env` and `infra/.env` must use the same MySQL credentials.

---

## Docker Compose (Production)

Build and run all services:

```bash
cd infra
docker compose up -d --build
```

Stop services:

```bash
docker compose down
```

### Services

- **mysql**: Database (port 3306)
- **backend**: FastAPI + Alembic migrations (port 3000)
- **frontend**: Nginx proxy & frontend (port 80)

---

## Deployment to VPS

### 1. Prepare Server

- Install Docker Engine and Docker Compose
- Open port 80 on firewall
- Clone repository

### 2. Configure Environment

```bash
cd infra
cp .env.example .env
```

Edit `.env` and update these critical values:

- `MYSQL_ROOT_PASSWORD` – strong random password
- `MYSQL_PASSWORD` – strong random password  
- `AUTH_TOKEN_SECRET` – strong random 32+ character secret
- `CORS_ORIGIN` – your domain (e.g., `https://links.example.com`)

### 3. Start Production Stack

```bash
docker compose up -d --build
```

Migrations run automatically on backend startup.

### 4. Create Admin User

```bash
docker compose exec backend python -m app.scripts.create_user [username] [password]
```

### 5. Verify Deployment

- ✅ Frontend loads: `https://your-domain.com/`
- ✅ API responds: `https://your-domain.com/api/health`
- ✅ Login works and redirects to `/links/search`

---

## Backup & Restore

### Backup MySQL

**Windows:**
```powershell
cd infra
docker compose exec mysql sh -c 'mysqldump -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' > backup.sql
```

**Mac/Linux:**
```bash
cd infra
docker compose exec mysql sh -c 'mysqldump -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' > backup.sql
```

### Restore MySQL

**Windows:**
```powershell
Get-Content backup.sql | docker compose exec -T mysql sh -c 'mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"'
```

**Mac/Linux:**
```bash
cat backup.sql | docker compose exec -T mysql sh -c 'mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"'
```

---

## Testing

### Run Backend Tests

```bash
cd backend
python -m pytest
```

Current coverage includes:

- ✅ Authentication service and routes
- ✅ Links management service and routes
- ✅ Category catalog and read-later flows
- ✅ Invalid JSON handling and validation
- ✅ Session cookie flow and CRUD operations
- ✅ Alembic migrations (manual)
- ✅ Admin CLI scripts (manual)

See [docs/e2e-checklist.md](docs/e2e-checklist.md) for end-to-end validation steps.

---

## Limitations

- ❌ No public user registration API
- ❌ No advanced role-based access control (RBAC)
- ❌ Simple signed session cookies (no external OAuth)
- ❌ No built-in TLS (use reverse proxy or cloud provider)
- ❌ No E2E browser test suite

---

## License

This project is provided as-is for educational and personal use.
- no full browser E2E suite
- deploy assumes HTTP unless TLS is terminated in front of Nginx
