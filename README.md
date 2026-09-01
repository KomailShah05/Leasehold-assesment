# Leasehold enquiry triage

A prototype that helps someone with a leasehold question describe their situation and get a
clearer next step. It signposts to guidance; it does not give legal advice.

Written for the LEASE take-home exercise. See [docs/PLAN.md](docs/PLAN.md) for the planning pack,
including scope, ordered tickets, risks and deliberate exclusions.

## Current state

Tickets 1 and 2. The app boots, the React frontend can reach the Django API, and the routes and
sample guidance content exist. The triage API and the user journey are not built yet.

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
python manage.py seed_guidance
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

## The content

Three routes — service charges, lease extensions, repairs — plus a fallback for anything else.

`backend/triage/content.py` holds **routing only**: the scenarios, the one follow-up question
each asks, and which `guidance_key` each answer points at. It is plain frozen dataclasses with no
Django imports, so the taxonomy reads top to bottom in one sitting and can be tested without
booting Django.

`guidance.GuidancePage` holds **the words**, in Wagtail, so LEASE editors own them.
`python manage.py seed_guidance` creates the eight sample pages and is safe to re-run.

Two things about that content:

- **It is not LEASE's published wording.** Every summary is original placeholder text written for
  this exercise, phrased as a *possible next step* rather than advice. Each page carries a
  `lease_url` so the app links out and the authoritative guidance stays LEASE's.
- **`lease_url` is currently the advice guide index**, not a deep link. lease-advice.org blocks
  automated requests, so I could not verify specific page URLs; guessing at them would risk
  sending a stressed person to a 404. It is an editor-managed field, which is where that decision
  belongs anyway.

Every "I'm not sure" answer routes to the adviser page rather than to a best guess. Guessing at
someone's situation is worse than handing them to a person.

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
- **Django owns routing, Wagtail owns wording.** The triage rules never contain guidance prose;
  they produce a `guidance_key` that resolves to an editor-owned page. So the words someone
  finally reads have been through an editor, not through a developer or a language model.
- **Guidance summaries are plain text, not rich text.** React renders them as text, so there is no
  path from editor content to markup in the browser.
- **The Wagtail scaffold was pruned.** The generated `search` app, welcome page and demo assets
  were deleted, because React owns the user-facing journey and Wagtail is only there to hold
  guidance content for editors.

## Not included, on purpose

No accounts, no contact fields, no analytics, no stored enquiry history, no deployment setup.
Free text will be processed for the current request and not persisted.

## AI usage

Recorded as the work progresses and written up in full at the end, covering what AI helped with,
what I changed or rejected, and what I verified myself.
