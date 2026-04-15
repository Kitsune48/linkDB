# LinkDB Frontend

React + TypeScript frontend for LinkDB with Vite, Tailwind CSS, and TypeScript for type safety.

## Requirements

- Node.js 18+
- npm or yarn
- Backend running on `http://localhost:3000` (development)

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Setup

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

For local development, `.env` should contain:

```env
VITE_API_BASE_URL=http://localhost:3000
```

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173` (Vite default).

### 4. Build for Production

```bash
npm run build
```

Output in `dist/` directory.

---

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:3000` (dev) or empty (production) |

**Production Note:** When using Nginx reverse proxy (as in production), leave `VITE_API_BASE_URL` empty since the frontend requests `/api/*` paths directly to Nginx, which proxies them to the backend.

---

## Project Structure

```
src/
├── main.tsx                # Entry point
├── App.tsx                 # Root component
├── index.css               # Global styles
├── api/
│   ├── client.ts           # Axios instance with defaults
│   ├── auth.ts             # Authentication endpoints
│   ├── links.ts            # Links endpoints
│   ├── categories.ts       # Categories endpoints
│   ├── read-later.ts       # Read Later endpoints
│   └── types.ts            # API response types
├── pages/
│   ├── LoginPage.tsx       # Login form and authentication
│   ├── SearchLinksPage.tsx # Main links search and filter
│   ├── NewLinkPage.tsx     # Create new link
│   └── ReadLaterPage.tsx   # Personal read later list
├── components/
│   ├── layout/
│   │   ├── AppLayout.tsx   # Main layout wrapper
│   │   └── Header.tsx      # Navigation header
│   ├── links/
│   │   ├── LinkCard.tsx    # Single link display
│   │   ├── LinkForm.tsx    # Link creation/editing
│   │   ├── LinksFilters.tsx # Filter controls
│   │   ├── CategoryMultiSelect.tsx # Category selector
│   │   └── Pagination.tsx  # Pagination controls
│   ├── routing/
│   │   └── PrivateRoute.tsx # Protected route wrapper
│   └── ui/
│       └── Badge.tsx       # Category badge component
├── hooks/
│   ├── useAuth.ts          # Authentication context hook
│   └── useCategoryOptions.ts # Category dropdown data
└── state/
    └── AuthProvider.tsx    # Global auth state provider
```

---

## Key Features

### Authentication

- Session-based auth with secure HTTP-only cookies
- Login page redirects unauthenticated users
- `AuthProvider` manages global auth state
- `useAuth()` hook provides auth context in components

### Links Management

- **Search Page** (`/links/search`)
  - Search and filter links by category, date
  - Edit or delete own links
  - Add/remove items from Read Later list
  - Pagination support

- **New Link Page** (`/links/new`)
  - Create new links with URL and categories
  - Form validation and error handling

- **Read Later Page** (`/links/read-later`)
  - Personal watch-list for each user
  - Manage items in the list

### Styling

- **Tailwind CSS** for utility-first styling
- Responsive design (mobile-first)
- **PostCSS** for processing

---

## Development

### Useful Scripts

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Type check (if using tsc)
npm run type-check
```

### Import Path Aliases

Configure TypeScript path aliases in `tsconfig.app.json` for cleaner imports:

```typescript
// Instead of
import { useAuth } from '../../../hooks/useAuth';

// Use
import { useAuth } from '@/hooks/useAuth';
```

Update `tsconfig.app.json`:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

---

## Styling Guidelines

- Use **Tailwind CSS** utility classes for styling
- Define reusable components in `components/` folder
- Avoid inline styles
- Keep components small and focused

### Example Component

```tsx
// src/components/ui/Button.tsx
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

export function Button({ children, onClick, disabled }: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
    >
      {children}
    </button>
  );
}
```

---

## API Integration

### Client Setup

All API calls use a configured Axios instance in `src/api/client.ts`:

```typescript
import { client } from '@/api/client';

// Automatic request/response handling
const response = await client.get('/links', {
  params: { category: 'web', page: 1 }
});
```

### Type Safety

API responses are typed in `src/api/types.ts`:

```typescript
interface Link {
  id: string;
  url: string;
  title: string;
  categories: Category[];
  isInReadLater: boolean;
}
```

---

## Authentication Flow

1. User submits login form → `POST /api/auth/login`
2. Backend returns session cookie (HttpOnly)
3. `AuthProvider` updates global auth state
4. Authenticated requests include cookie automatically
5. Protected routes redirect unauthenticated users to login

---

## Deployment

### Docker

Build Docker image:

```bash
docker build -t linkdb-frontend .
docker run -p 80:80 linkdb-frontend
```

The `Dockerfile` includes:

1. Node.js build stage (compile React + Vite)
2. Nginx serve stage (optimized production server)
3. Nginx proxy configuration for `/api/*` routes

### Nginx Configuration

See `nginx/default.conf` for proxy setup:

- `/api/*` requests proxied to backend
- Static assets served from `dist/`
- SPA routing handled correctly

---

## Troubleshooting

**"Can't connect to backend"**
- Check `VITE_API_BASE_URL` in `.env`
- Verify backend is running on port 3000
- Check browser console for CORS errors

**"Login fails"**
- Check credentials in backend
- Verify `CORS_ORIGIN` in backend `.env` includes frontend URL
- Check network tab in DevTools for error response

**"Styling not applied"**
- Run `npm install` to ensure Tailwind is installed
- Restart dev server after `.env` changes
- Check Tailwind config in `tailwind.config.js`

---

## See Also

- [Main README](../README.md) for full project setup
- [Backend README](../backend/README.md) for API documentation
- [E2E Checklist](../docs/e2e-checklist.md) for deployment verification
