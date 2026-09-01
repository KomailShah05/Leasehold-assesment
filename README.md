# Leasehold enquiry triage

A prototype that helps someone with a leasehold question describe their situation and get a
clearer next step. It signposts to guidance; it does not give legal advice.

Written for the LEASE take-home exercise. See [docs/PLAN.md](docs/PLAN.md) for the planning pack,
including scope, ordered tickets, risks and deliberate exclusions.

## Current state

Tickets 1 to 6. The journey works end to end, handles being got wrong, and has been checked
against WCAG 2.2 AA by keyboard and by measurement. Tests and the write-up are still to come.

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

Six routes — service charges, lease extensions, repairs, management problems, right to manage and
fire safety — plus a fallback for anything else. The plan originally scoped three; the other three
were added once real LEASE section URLs were available. The cost is a longer first screen, which is
the main thing to watch if the list grows again.

`backend/triage/content.py` holds **routing only**: the scenarios, the one follow-up question
each asks, and which `guidance_key` each answer points at. It is plain frozen dataclasses with no
Django imports, so the taxonomy reads top to bottom in one sitting and can be tested without
booting Django.

`guidance.GuidancePage` holds **the words**, in Wagtail, so LEASE editors own them.
`python manage.py seed_guidance` creates the twenty sample pages and is safe to re-run.

Two things about that content:

- **It is not LEASE's published wording.** Every summary is original placeholder text written for
  this exercise, phrased as a *possible next step* rather than advice. Each page carries a
  `lease_url` so the app links out and the authoritative guidance stays LEASE's.
- **`lease_url` points at real LEASE section pages**, supplied rather than guessed, with tracking
  parameters stripped. lease-advice.org returns 403 to every automated request, so no URL here was
  discovered by crawling. The three lease extension pages still point at the home page because no
  verified URL for that section was available, and an unchecked deep link risks a 404 at the moment
  a person least needs one. The field is editor-managed, so LEASE can correct those in Wagtail
  without a code change.
- **No LEASE wording is reproduced.** Every summary is original text written for this exercise and
  phrased as a possible next step. Their published guidance is both copyrighted and authoritative;
  copying it in would turn signposting into advice.

Every "I'm not sure" answer routes to the adviser page rather than to a best guess. Guessing at
someone's situation is worse than handing them to a person.

## The API

Two endpoints, both under `/api/`.

`GET /api/triage/routes/` returns the scenario options, so the React app never hardcodes copy.
"I am not sure" comes back in the same list, because it belongs in the same radio group.

`POST /api/triage/` takes `scenario`, `description` and `answerId`, all optional, and returns one
of three shapes distinguished by `status`:

- `question` — we have a route and need one follow-up answer
- `outcome` — a possible next step, with guidance from Wagtail
- `fallback` — we could not place the problem, so here is a route to a person

Clients switch on `status`. There are no nullable fields to probe.

### How a route is decided

`backend/triage/services.py` holds the rules as pure functions with no Django imports, so they can
be tested without a database.

A chosen scenario always wins: if someone has told us what their problem is about, we do not
second-guess them. Free text is scored against each route's keywords, where longer phrases count
for more than single words — "lease extension" is evidence, "lease" alone is not, since nearly
every visitor will type it.

We refuse to name a route in three separate situations, all of which go to the fallback: nothing
matched, the best match was too weak (`MINIMUM_SCORE`), or two routes were too close to separate
(`MINIMUM_LEAD`). A tie is never broken by picking the first one.

When a route is *inferred* from free text rather than chosen, its follow-up question gains one
extra answer — "This is not what my problem is about" — which goes to the fallback. So a wrong
guess costs one click to correct, and correcting us takes the same effort as agreeing with us.
That is why there is no separate "did we get this right?" screen: it would add a step for someone
who is already stressed.

Also fallback, not an error: an unknown scenario, and an outcome whose guidance page is missing or
unpublished. Someone seeing the fallback is already having a bad day; a 500 would not help.

## The journey

Three steps. `useTriage` holds all the state and every API call, so `App.tsx` only decides which
step belongs on screen and the components do nothing but render what they are given.

The steps are composed from small pieces rather than repeating markup: `RadioGroup` is used by
both question screens, so hit areas, label wiring and error handling cannot drift apart between
them, and `FieldError`, `ErrorAlert`, `GuidanceCard`, `DescriptionField` and `SubmitButton` each
do one thing. The largest file in the frontend is 100 lines.

**Choosing a scenario.** Radio buttons in a `fieldset`, not a dropdown, because a dropdown hides
its options until you work out you have to open it. "I am not sure" is the fourth radio in the
same group rather than a link off to one side, so it costs no more effort than the other three.
The legal phrase sits *inside* each label in smaller text, so a screen reader announces it along
with the plain wording instead of it being visual-only.

**The follow-up question.** When the route was inferred from someone's own words we say so
plainly — "this looks like it may be about…" — rather than presenting the guess as fact, and the
answer list carries the option that tells us we were wrong.

**The result.** Outcomes and fallbacks are framed identically: a possible next step, a link to the
authoritative LEASE page, and a line saying this is not legal advice. "Start again" clears
everything.

Nothing is written to storage. What someone types is used for the request and then forgotten.

## When things go wrong

**Validation happens in the browser first.** An empty form is answered immediately and never
becomes a request. The message names what to do — "Choose one of the options, or describe the
problem in your own words" — rather than reporting that something is invalid. Errors clear as soon
as the person acts, so the page stops telling them off once they have fixed it. The server still
validates everything independently; the client check is for speed of feedback, not for safety.

**Errors are not signalled by colour alone.** Each one is bold, worded plainly, and sits directly
above the control it is about, linked with `aria-describedby` and marked `aria-invalid`.

**A failing service gets a retry, not a dead end.** API errors appear in a `role="alert"` region
with a "Try again" button that resends the last attempt, so a dropped connection does not cost
someone their description. Retry is offered only for failures that might pass on a second attempt:
a validation error is about what was entered, so retrying it unchanged would just fail again.

**Requests time out after ten seconds.** `fetch` has no timeout of its own, so without this a
stalled request leaves someone watching a "Checking…" button indefinitely. Ten seconds is long
enough for a slow connection and short enough to admit defeat while they are still paying
attention.

**Starting again clears everything** — the result, the errors and the retained request.

## Where a language model could fit, and where it must not

Triage is deterministic. Picking a category is the one part a model could plausibly do better, so
it sits behind a `Classifier` interface in `backend/triage/classifier.py`. `KeywordClassifier` is
what ships; `match_route` takes any implementation as an argument, so a model-backed one could be
swapped in without touching the questions, the guidance or the fallback.

**The interface is deliberately narrow: a classifier returns a route id or `None`. It cannot
return text.** No implementation of it, model-backed or otherwise, can put words in front of a
person that an editor has not approved. That is what keeps "we signpost, we do not advise" true
regardless of what is plugged in.

Returning `None` is a real answer rather than a failure, so any classifier must be willing to give
it. And a chosen scenario always overrides the classifier: if someone has told us what their
problem is about, nothing gets to second-guess them.

I decided against having a model **write** the guidance a person reads, even labelled as an AI
suggestion. A model asked what someone should do about their lease will produce something that
reads as legal advice, because that is what the question invites, and a worried person reads the
answer rather than the disclaimer. It would also put an external service in the core flow and send
free text that may contain personal details to a third party. The classifier boundary gets the
benefit of a model without any of that.

## Accessibility

Checked by keyboard and by measuring the rendered page, not by eye.

**Focus is moved deliberately, and only twice.** When a step changes, focus goes to the new
question or result heading, so a keyboard or screen reader user is taken to the content that
replaced what they were reading instead of being stranded at a button that no longer exists. When
validation fails, focus goes to the message. It is *not* taken on first load, where stealing focus
from the top of the page would be wrong.

**Errors are announced once, not twice.** Field errors move focus, which announces them, so they
are deliberately not `role="alert"` — doing both would read the same message out twice. The API
error is the reverse: it is `role="alert"` and does not take focus, because the person may be
mid-sentence in the description box.

**Measured against WCAG 2.2 AA:**

| Check | Result |
| --- | --- |
| Text contrast | 6.7:1 to 17.4:1, all above the 4.5:1 minimum |
| Choice border (1.4.11) | Was **2.08:1 and failing**; darkened to 3.51:1 |
| Focus ring (1.4.11) | 3px solid, 6.7:1 against the page |
| Target size (2.5.8) | Smallest interactive target 117x54, above the 24x24 minimum |
| Keyboard | Tab reaches the group, arrow keys move and select within it, Tab exits to the next field |
| Reflow | No horizontal scrolling at 375px |

Also handled: `prefers-reduced-motion`, Windows forced-colors mode, and a chosen row that changes
its whole background rather than relying on the small circle alone.

**Known gap:** this has not been tested with a real screen reader, only against the accessibility
tree and computed styles. A genuine VoiceOver or NVDA pass is the next thing I would do.

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
