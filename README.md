# Personal Knowledge Base / Notes App

**Stack:** Next.js 14 (App Router) + TypeScript · Flask · PostgreSQL · Docker · JWT · Alembic

A production-oriented foundation project that teaches the complete modern stack wiring.

## Features

- Markdown notes with live preview
- Tags (many-to-many) + nested folders
- Full-text search (title + content)
- JWT authentication
- File uploads / attachments
- Docker Compose multi-service setup
- Type-safe API contracts (TypeScript ↔ Python/Pydantic)
- Alembic migrations
- Health checks, volumes, networking

## Project Structure

```
notes-app/
├── docker-compose.yml          # All services
├── .env.example
├── README.md
├── frontend/                   # Next.js 14 + TypeScript
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.mjs
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── src/
│       ├── app/                # App Router
│       │   ├── (auth)/login
│       │   ├── (auth)/register
│       │   ├── notes/
│       │   │   ├── page.tsx    # List + search
│       │   │   └── [id]/       # Editor + preview
│       │   ├── layout.tsx
│       │   └── page.tsx
│       ├── components/
│       ├── lib/
│       │   ├── api.ts          # Typed API client
│       │   ├── auth.ts
│       │   └── utils.ts
│       └── types/
└── backend/                    # Flask API
    ├── Dockerfile
    ├── requirements.txt
    ├── wsgi.py
    ├── app/
    │   ├── __init__.py         # App factory
    │   ├── config.py           # Pydantic settings
    │   ├── extensions.py
    │   ├── models.py           # SQLAlchemy 2.0 models
    │   └── routes/
    │       ├── auth.py
    │       ├── notes.py
    │       ├── folders.py
    │       ├── tags.py
    │       └── attachments.py
    └── migrations/             # Alembic
```

## Quick Start (Docker — recommended)

```bash
# 1. Clone / enter the project
cd notes-app

# 2. Create environment file
cp .env.example .env

# Edit .env and set strong secrets:
# JWT_SECRET_KEY=your-long-random-string-at-least-32-chars
# SECRET_KEY=another-long-random-string

# 3. Start everything
docker compose up --build

# Services:
# - Frontend  → http://localhost:3000
# - Backend   → http://localhost:5000
# - Postgres  → localhost:5432
# - Redis     → localhost:6379
```

The backend automatically runs `flask db upgrade` on startup.

### First use

1. Open http://localhost:3000
2. Register a new account
3. Create notes, folders, tags, upload files

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start Postgres + Redis yourself (or use docker compose up db redis)
export DATABASE_URL=postgresql://notes:notes_secret@localhost:5432/notes_db
export JWT_SECRET_KEY=dev-secret-change-me
export FLASK_APP=wsgi.py

flask db init          # only first time
flask db migrate -m "initial"
flask db upgrade

flask run --host=0.0.0.0 --port=5000
# or: gunicorn -b 0.0.0.0:5000 --reload wsgi:app
```

### Frontend

```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:5000 npm run dev
```

## API Overview

| Method | Endpoint                        | Description              |
|--------|---------------------------------|--------------------------|
| POST   | /api/auth/register              | Create account           |
| POST   | /api/auth/login                 | Login → JWT              |
| GET    | /api/auth/me                    | Current user             |
| GET    | /api/notes?q=&folder_id=&tag_id=| List / search notes      |
| POST   | /api/notes                      | Create note              |
| GET    | /api/notes/:id                  | Get note                 |
| PUT    | /api/notes/:id                  | Update note              |
| DELETE | /api/notes/:id                  | Delete note              |
| GET/POST/PUT/DELETE | /api/folders          | Folder CRUD              |
| GET/POST/DELETE     | /api/tags               | Tag CRUD                 |
| POST   | /api/attachments/notes/:id      | Upload file              |
| GET    | /api/attachments/:id/download   | Download file            |

All endpoints (except auth) require:

```
Authorization: Bearer <access_token>
```

## Database Schema

- **users** — email, username, password_hash
- **folders** — nested via parent_id
- **tags** — unique per user
- **notes** — markdown content, pinned/archived flags
- **note_tags** — many-to-many
- **attachments** — file metadata + local storage

## Production Notes

1. Change all secrets in `.env`
2. Set `FLASK_ENV=production` and `DEBUG=False`
3. Use a real volume or S3 for uploads
4. Put a reverse proxy (Traefik / Caddy / Nginx) in front
5. Enable HTTPS
6. Consider rate limiting + Redis for token blacklist if needed
7. Multi-stage Docker builds are already present

## What you learn from this project

- Clean multi-service Docker Compose with healthchecks & volumes
- Flask application factory + blueprint architecture
- SQLAlchemy 2.0 typed models + Alembic
- JWT auth flow (Flask-JWT-Extended)
- Type-safe frontend API client
- Next.js 14 App Router + client components
- Markdown editing + preview
- File upload handling
- CORS, environment management, and deployment readiness

Happy building!
