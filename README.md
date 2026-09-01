# Leasehold enquiry triage

A prototype that helps someone with a leasehold question describe their situation and get a
clearer next step. It signposts to guidance; it does not give legal advice.

Written for the LEASE take-home exercise.

| | |
| --- | --- |
| [docs/PLAN.md](docs/PLAN.md) | The planning pack: scope, ordered tickets, risks, exclusions |
| [docs/REVIEW.md](docs/REVIEW.md) | Hardening pass, personal data and security, accessibility, self code review |
| [docs/AI-USAGE.md](docs/AI-USAGE.md) | What AI helped with, what I changed or rejected, what was verified |

## What it does

Someone either picks a familiar scenario or describes the problem in their own words. A
deterministic rule set decides which of six topics it belongs to, asks one follow-up question, and
shows a possible next step drawn from guidance an editor wrote, with a link out to LEASE.

When it cannot tell, it says so and offers an adviser rather than guessing.

## Running it

Requires Python 3.12+ (Django 5.2 and Wagtail 7 need it) and Node 20+.

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export DJANGO_SETTINGS_MODULE=config.settings.dev
python manage.py migrate && python manage.py seed_guidance && python manage.py runserver
```

```bash
cd frontend && npm install && npm run dev
```

The app is on <http://localhost:5173> and needs the API on <http://localhost:8000>. The Wagtail
admin is at `/admin/` — `python manage.py createsuperuser` for a login.

## Checking it

```bash
./scripts/test.sh
```

Runs both test suites and both linters: 65 backend tests, 14 frontend, ruff, TypeScript, oxlint.

## How it is put together

```text
React  →  typed API client  →  Django view  →  triage service  →  Wagtail guidance
```

**Django owns routing, Wagtail owns wording.** The triage rules never contain guidance prose; they
produce a `guidance_key` that resolves to an editor-owned page. So the words someone finally reads
have been through an editor, not a developer or a language model.

**The rules are pure functions.** `backend/triage/classifier.py` and `services.py` have no Django
imports, so the whole taxonomy can be read in one sitting and tested without a database.

**Responses are a typed union** — `question`, `outcome` or `fallback`. Clients switch on `status`
rather than probing nullable fields.

**Refusing to answer is the important behaviour.** A route is only named when something matched,
the match was strong enough, and no second route was close. Nothing matched, too weak, too close to
call, the person saying we guessed wrong, or a missing guidance page all end in the same honest
fallback. That is what most of the tests are about: a confidently wrong route sends someone who is
already worried down a path that does not fit their problem.

**The frontend has two runtime dependencies**, `react` and `react-dom`. No router, no data-fetching
library, no CSS framework. Components never call `fetch`; everything goes through
`frontend/src/api/client.ts`, which turns every failure into one shape.

## Decisions worth knowing

- **Deterministic rules, not a model.** Reproducible, testable without a network, no hallucination,
  and no third party in the core flow. Category matching sits behind a `Classifier` interface that
  returns a route id and *cannot return text*, so a model-backed version could never put unapproved
  words in front of a person.
- **Scope grew from three routes to six** once real LEASE section URLs were available. The cost is
  a longer first screen, which is the main thing I would revisit. `docs/PLAN.md` records the change.
- **No LEASE wording is reproduced.** Every summary is original and phrased as a possible next step;
  each links out so the authoritative guidance stays theirs.
- **Nothing is stored.** No accounts, no contact fields, no analytics, no enquiry history. Free text
  is used for the request and discarded, and a test asserts nothing is written.
- **CORS uses an explicit origin list**, never `CORS_ALLOW_ALL_ORIGINS`. Production settings read
  `DJANGO_SECRET_KEY` with no fallback, and `manage.py check --deploy` passes clean.

## Left out on purpose

No authentication, deployment setup, saved enquiries, analytics, or CMS work beyond the guidance
model. Details and the remaining gaps are in [docs/REVIEW.md](docs/REVIEW.md).
