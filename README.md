# Leasehold Enquiry Triage

A small prototype for the LEASE take-home exercise.

It helps someone with a leasehold question describe their situation or choose a common scenario,
then guides them to a relevant next step in plain English. It provides signposting only, not legal
advice.

|                              |                                                    |
| ---------------------------- | -------------------------------------------------- |
| [Plan](docs/PLAN.md)         | Scope, assumptions, tasks and risks                |
| [Review](docs/REVIEW.md)     | Hardening, accessibility, security and self-review |
| [AI usage](docs/AI-USAGE.md) | How AI was used and what was verified              |

## What it does

1. Choose a common scenario or describe the problem in your own words.
2. Answer one follow-up question.
3. Receive a plain-English next step with a link to LEASE guidance.

The prototype covers six topics and uses a safe fallback when it cannot confidently identify the
issue.

## Tech stack

* **Frontend:** React 19, TypeScript, Vite
* **Backend:** Django 5.2, plain views returning JSON
* **Content:** Wagtail 7
* **Database:** SQLite for local development

```text
React → API client → Django → Triage rules → Wagtail guidance
```

The frontend does not contain guidance content. Django handles the triage flow, while Wagtail
provides editor-managed guidance.

There is no REST framework. Two endpoints returning fixed shapes did not need one, and leaving it
out keeps the request path short enough to read end to end. The frontend has two runtime
dependencies, `react` and `react-dom`.

## Run locally

Requirements: **Python 3.12+** and **Node 20+**.

### Backend

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

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.
The API runs on `http://localhost:8000`.

To access the Wagtail admin:

```bash
python manage.py createsuperuser
```

Then visit `http://localhost:8000/admin/`.

## Tests and checks

Run the full test and lint suite with:

```bash
./scripts/test.sh
```

This runs the backend and frontend tests plus the configured lint and type checks: 79 tests, 65
backend and 14 frontend.

## Key decisions

* **Deterministic triage:** keyword rules are predictable, testable and do not depend on an external
  service.
* **Safe fallback:** ambiguous or unsupported situations are not given a confident category.
* **Editor-owned guidance:** guidance text lives in Wagtail rather than in the triage rules.
* **Privacy by default:** no accounts, contact details, analytics or enquiry history. Free-text input
  is not stored.
* **Accessibility:** semantic HTML, keyboard support, focus management, clear errors and
  WCAG-focused checks.

## Deliberately left out

This is a prototype, not a production advice service. It does not include authentication, saved
enquiries, analytics, deployment infrastructure, or a full CMS.

The original plan started with three topics and grew to six during development. The longer first
screen is a known trade-off and is documented in the review.

See [docs/REVIEW.md](docs/REVIEW.md) for known gaps and what I would improve next.

**Komail Shah — 1 September 2026**
