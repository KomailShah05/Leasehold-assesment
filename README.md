# Leasehold enquiry triage

A prototype that helps someone with a leasehold question describe their situation and get a
clearer next step. It signposts to guidance; it does not give legal advice.

Written for the LEASE take-home exercise. See [docs/PLAN.md](docs/PLAN.md) for the planning pack,
including scope, ordered tickets, risks and deliberate exclusions.

## Current state

Ticket 1 (project setup) only. The app boots, the React frontend can reach the Django API, and
the tooling is wired up. The triage journey itself is not built yet.

## What is here

| Path | What it is |
| --- | --- |
| `backend/` | Django 5.2 project (`config`) with Wagtail 7 for guidance content, SQLite for local use. |
| `frontend/` | Vite + React 19 + TypeScript app in strict mode. |
| `docs/` | The plan and the two diagrams. |

## Requirements

- Python 3.12 or newer (Django 5.2 and Wagtail 7 do not support 3.9)
- Node 20 or newer

## Running the backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
export DJANGO_SETTINGS_MODULE=config.settings.dev
python manage.py migrate
python manage.py runserver
```

The API is then on <http://localhost:8000>, with a health check at
<http://localhost:8000/api/health/> and the Wagtail admin at <http://localhost:8000/admin/>.
Create an editor login with `python manage.py createsuperuser`.

## Running the frontend

```bash
cd frontend
npm install
npm run dev
```

The app is then on <http://localhost:5173> and expects the backend to be running.

## Checks

```bash
cd backend && .venv/bin/ruff check . && .venv/bin/ruff format --check .
```

```bash
cd frontend && npm run build && npm run lint
```

Tests arrive with ticket 7; `pytest` is installed and configured but there is nothing to run yet.

## Decisions worth knowing

- **Two runtime frontend dependencies**, `react` and `react-dom`. No router, no data-fetching
  library, no CSS framework. The journey is a handful of steps held in local React state, so the
  dependency list stays small enough to defend.
- **Components never call `fetch`.** Everything goes through `frontend/src/api/client.ts`, which
  turns every failure into one `ApiError` shape so the UI has a single error path to handle.
- **CORS uses an explicit origin list** from `CORS_ALLOWED_ORIGINS`, never
  `CORS_ALLOW_ALL_ORIGINS`.
- **Secrets come from the environment.** Development has a throwaway key; the production settings
  read `DJANGO_SECRET_KEY` with no fallback, so a missing key stops the deploy instead of starting
  the site with a guessable secret.
- **The Wagtail scaffold was pruned.** The generated `search` app, welcome page and demo assets
  were deleted, because React owns the user-facing journey and Wagtail is only there to hold
  guidance content for editors.

## Not included, on purpose

No accounts, no contact fields, no analytics, no stored enquiry history, no deployment setup.
Free text will be processed for the current request and not persisted.

## AI usage

Recorded as the work progresses and written up in full at the end, covering what AI helped with,
what I changed or rejected, and what I verified myself.
