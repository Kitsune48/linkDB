# LinkDB E2E Checklist

This checklist covers the main backend + frontend flows without requiring a full browser automation suite.

## Preparation

1. Start MySQL:
   ```bash
   cd infra
   docker compose up -d mysql
   ```
2. Install backend dependencies and run migrations:
   ```bash
   cd ../backend
   python -m pip install -e .[dev]
   alembic upgrade head
   ```
3. Create at least two users:
   ```bash
   python -m app.scripts.create_user mario SuperPassword123
   python -m app.scripts.create_user alice AnotherPassword456
   ```
4. Start backend and frontend in two terminals:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
   ```
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Backend core

1. `POST /api/auth/login` with valid credentials:
   Expected: `200`, session cookie set.
2. `POST /api/auth/login` with wrong password:
   Expected: `401 INVALID_CREDENTIALS`.
3. `GET /api/auth/me` without cookie:
   Expected: `401 UNAUTHENTICATED`.
4. `POST /api/links` with valid session:
   Expected: `201`, link created with correct `addedBy`.
5. `PATCH /api/links/:id` as owner:
   Expected: `200`, fields updated.
6. `PATCH /api/links/:id` as another user:
   Expected: `403 FORBIDDEN`.
7. `DELETE /api/links/:id` as owner:
   Expected: `200`, success message.
8. `GET /api/links?q=...&category=...&status=...&addedBy=...`:
   Expected: coherent results and correct `meta`.

## Frontend core

1. Open `http://localhost:5173/login`.
   Expected: login form visible.
2. Submit empty form.
   Expected: inline username/password errors.
3. Login with wrong credentials.
   Expected: credentials error message.
4. Login with valid credentials.
   Expected: redirect to `/links`, username visible in the header.
5. Reload `/links`.
   Expected: session restored through `/api/auth/me`.
6. Create a new link from the top form.
   Expected: success message, form reset, new link visible in the list.
7. Filter by search, category and status.
   Expected: updated list and coherent pagination.
8. Enable `Added by me`.
   Expected: only authenticated user links remain.
9. Edit an owned link.
   Expected: inline editor, successful save, refreshed list.
10. Delete an owned link.
    Expected: confirmation, successful delete, link removed.
11. Sign in as another user.
    Expected: `Edit` and `Delete` are hidden on non-owned links.

## Automated backend tests

```bash
cd backend
python -m pytest
```
