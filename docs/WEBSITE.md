# Website Frontend

## Overview

The website is a public-facing React application built with Vite, TypeScript, and Tailwind CSS. It serves as the primary user interface for IdeaLab AI, offering both public content browsing and authenticated dashboards.

## Running

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Tech Stack

- React 19
- TypeScript 6.0
- Vite 8.3
- Tailwind CSS 4.3
- TanStack React Query 5.x
- React Router DOM 7.x

## Pages

### Public Pages (no auth required)

| Route | Component | Description |
|---|---|---|
| `/` | Home | Landing page with feature highlights |
| `/about` | About | IdeaLab philosophy, process, participation |
| `/events` | Events | Upcoming & past events grid |
| `/events/:id` | EventDetail | Single event detail view |
| `/projects` | Projects | Published project cards |
| `/projects/:id` | ProjectDetail | Single project detail view |
| `/people` | People | Faculty, members, staff directory |
| `/facilities` | Facilities | Equipment catalog |
| `/facilities/:id` | EquipmentDetail | Single equipment detail |
| `/achievements` | Achievements | Awards & impact |
| `/media` | Media | Documents & resources |
| `/contact` | Contact | Contact form & info |
| `/chat` | Chat | AI text assistant |
| `/login` | Login | Auth form |
| `/register` | Register | Registration form |

### Dashboard Pages (auth required)

| Route | Component | Description |
|---|---|---|
| `/dashboard` | Dashboard | Overview with stats |
| `/dashboard/events` | EventsDashboard | CRUD for events |
| `/dashboard/projects` | ProjectsDashboard | CRUD for projects |
| `/dashboard/people` | PeopleDashboard | View faculty, members, staff |
| `/dashboard/equipment` | EquipmentDashboard | View equipment |
| `/dashboard/documents` | DocumentsDashboard | View documents |
| `/dashboard/users` | UsersDashboard | User management (superuser) |
| `/dashboard/audit` | AuditDashboard | Audit logs (superuser) |
| `/dashboard/settings` | SettingsDashboard | System settings (superuser) |

## Key Components

### Navbar
- Sticky top navigation bar
- Links: Home, About, Events, Projects, People, Facilities, AI Assistant, Voice Assistant
- Dashboard link (only if authenticated)
- Sign in / Sign out button

### AuthContext
- Manages JWT tokens in `localStorage`
- Provides `login`, `register`, `logout`, `refreshToken`
- Auto-fetches `/auth/me` on page load if token exists

### RequireAuth / RequireSuperuser
- Route guards that redirect to `/login` if not authenticated
- Superuser guard additionally checks `user.is_superuser`

### API Client (`api/client.ts`)
- Wraps `fetch` with JSON error handling
- Attaches `Authorization: Bearer <token>` header
- Base URL from `VITE_API_URL` or `/api` (proxied to backend)

## State Management
- TanStack React Query for server-state caching
- AuthContext for client-side auth state
- localStorage for token persistence

## Styling
- Tailwind CSS with custom color palette:
  - `primary` (blue): `#0ea5e9`
  - `secondary` (purple): `#8b5cf6`
  - `accent` (orange): `#fd853a`

## Build

```powershell
npm run build
```

Output goes to `frontend/dist/`.