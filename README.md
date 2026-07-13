# Support CRM — Customer Support Ticketing System

A full-stack support ticket management system built with **FastAPI**, **SQLite (SQLAlchemy)**, and a
**vanilla JS + Tailwind CSS** frontend, served as a single deployable app.

## Features

- **Create tickets** — customer name, email, subject, description; auto-generated ticket ID (`TKT-001`, `TKT-002`, ...) and timestamp
- **List all tickets** — clean table view (ID, customer, subject, status, date)
- **Search-as-you-type** — across name, ticket ID, email, and description
- **Filter by status** — Open / In Progress / Closed
- **Ticket detail page** — full info, update status, add notes/comments (with history)

## Tech Stack

| Layer     | Choice                                   |
|-----------|-------------------------------------------|
| Backend   | Python + FastAPI                          |
| Database  | SQLite via SQLAlchemy ORM                 |
| Frontend  | HTML + Tailwind CSS (CDN) + Vanilla JS     |
| Deploy    | Railway.app (or any host that runs Uvicorn) |

The frontend is served directly by FastAPI (`StaticFiles`), so the whole app is **one deployable service** — no separate frontend host or CORS setup needed in production.

## Project Structure

```
support-crm/
├── app/
│   ├── main.py          # FastAPI app, routes, static file serving
│   ├── models.py        # SQLAlchemy models (Ticket, Note)
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── database.py       # DB engine/session setup
│   └── static/
│       ├── index.html    # Ticket list + search + filter + create modal
│       └── ticket.html   # Ticket detail + status update + notes
├── requirements.txt
├── Procfile              # start command for Railway/Render
├── .env.example
└── .gitignore
```

## Database Schema

**tickets**
| column           | type     |
|------------------|----------|
| id               | pk       |
| ticket_id        | unique, e.g. TKT-001 |
| customer_name    | text     |
| customer_email   | text     |
| subject          | text     |
| description      | text     |
| status           | Open / In Progress / Closed |
| created_at       | timestamp |
| updated_at       | timestamp |

**notes**
| column      | type              |
|-------------|-------------------|
| id          | pk                |
| ticket_id   | fk → tickets.ticket_id |
| note_text   | text              |
| created_at  | timestamp         |

## API Endpoints

| Method | Path                     | Description                          |
|--------|--------------------------|---------------------------------------|
| POST   | `/api/tickets`           | Create a ticket                       |
| GET    | `/api/tickets`           | List tickets (`?status=`, `?search=`) |
| GET    | `/api/tickets/{ticket_id}` | Get full ticket detail + notes      |
| PUT    | `/api/tickets/{ticket_id}` | Update status and/or add a note     |

## Local Setup

```bash
# 1. Clone and enter the repo
git clone <your-repo-url>
cd support-crm

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) copy env file — defaults work out of the box with SQLite
cp .env.example .env

# 5. Run the app
uvicorn app.main:app --reload

# App is now live at http://localhost:8000
```

The SQLite database file (`crm.db`) is created automatically on first run — no migrations needed.

## Deployment (Railway.app)

1. Push this repo to GitHub.
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**.
3. Railway auto-detects Python. Set the **start command** to:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
   (already provided in `Procfile`, Railway will pick it up)
4. No environment variables are required for the default SQLite setup.
5. Deploy — Railway gives you a public URL once the build finishes.

> Note: Railway's filesystem is ephemeral on redeploy, so the SQLite file resets when you redeploy.
> For a persistent production DB, set `DATABASE_URL` to a Postgres connection string (Railway can
> provision one for free) — the app already reads this env var in `database.py`.

## Design Decisions

- **Single-service deployment**: the FastAPI app serves both the API and the static frontend, so there's only one thing to deploy and no CORS friction.
- **Sequential ticket IDs**: generated from the row count with a collision check, matching the `TKT-001` format from the spec without needing a separate counter table.
- **Notes as a separate table**: keeps the ticket table clean and supports an unlimited note history per ticket.
- **Search-as-you-type**: debounced (250ms) client-side to avoid hammering the API on every keystroke.

## Possible Improvements (with more time)

- Authentication for support agents
- Pagination for large ticket lists
- Email notifications on status change
- Ticket priority levels and assignment to specific agents
