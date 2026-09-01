# AI usage

An honest account of what AI helped with, what I changed or rejected, and what was verified. Written
from the record of the working sessions rather than reconstructed afterwards.

## How it was used

I defined the architecture and the acceptance criteria for each ticket, then used Claude as a coding
pair to implement against them. Work went one ticket at a time, and each ticket was reviewed before
it was committed. The commit history reflects that order rather than being tidied up at the end.

What it was **not** used for: writing the application in one pass, generating any guidance a user
reads, or making product decisions.

## What it genuinely helped with

**Drafting code to a decided design.** The triage rules, the API layer, the React components and the
tests were drafted this way against decisions already made in the plan.

**Finding bugs by exercising the code rather than reading it.** Four real defects surfaced this way,
each of which would have survived a code review:

- The "this is not what my problem is about" answer returned an outcome still labelled with the
  route the person had just rejected. That is the fallback failing to fire, which is the highest-risk
  failure in this application.
- The legal term inside each radio label produced an accessible name with no space
  ("…bill or chargeService charges…"), so a screen reader ran two phrases together as one word. It
  looked perfect on screen.
- The choice border measured 2.08:1 against the page, failing WCAG 1.4.11, which needs 3:1. It also
  looked fine.
- Keyword matching was a plain substring test, so "bill" matched inside "billing".

**Plain-English wording.** Draft copy was consistently reworded to remove legal vocabulary and to
phrase every outcome as a possible next step. One line that had drifted into advice — telling the
reader to get advice early rather than waiting — was caught and rewritten to describe the option
instead.

**Test cases I would not have thought of.** In particular the guard that no keyword is shared between
two routes, since a shared word makes routes tie and ties go to the fallback: a regression that would
make triage quietly worse as it grew, with nothing visibly broken.

## What I changed or rejected

**Ambiguity handling.** It proposed sending any ambiguous free text straight to the fallback. I
rejected that in favour of taking the strongest match, asking the follow-up question, and falling
back only if still unclear — which is what the plan had said from the start.

**Generating advice with a language model.** It was suggested the fallback could produce an AI-written
suggestion labelled as such. I decided against it: a model asked what someone should do about their
lease will produce something that reads as legal advice, a worried person reads the answer rather
than the disclaimer, and it would put an external service and possibly personal free text into the
core flow. AI classification instead sits behind an interface that returns a route id and cannot
return text. That boundary is the point.

**Scraping LEASE's site for content.** Rejected. Their wording is copyrighted and is itself legal
guidance; copying it in would turn signposting into advising. All summary copy here is original and
every link goes out to their page. Their site also blocks automated access, so every URL was
gathered by hand.

**Scope.** It recommended staying at three routes. I chose to widen to six once real LEASE section
URLs were available. The plan records the change and the cost: a longer first screen.

**Uncertainty routing.** Every "I am not sure" answer originally resolved to one shared adviser page.
I wanted each to reach its own topic overview. That meant overriding a safety rule, so it was
replaced rather than deleted: uncertainty still cannot reach a confident specific outcome, and a test
now checks every overview page still names an adviser.

**Code style and structure.** I asked for arrow functions throughout, and for the journey to be
composed from small shared components rather than large step files.

**Dependencies.** I questioned using `fetch` rather than axios interceptors. We kept `fetch`: there is
no auth or token refresh here, which is what interceptors mainly buy, and the typed client already
gives one error shape. The one thing axios would have provided — a request timeout — was added
explicitly with `AbortSignal.timeout`. A proposal to make the database configurable through an
environment variable was declined as unnecessary for a prototype that is not being deployed.

## What was verified, and how

Verification was done by running things:

- **79 tests**, 65 backend and 14 frontend, all passing via `./scripts/test.sh`.
- **The tests were checked against deliberately broken code.** Reintroducing the escape-hatch bug
  failed one test; removing the ambiguity guard failed two; removing the over-sized body guard
  failed one.
- **Contrast and target sizes were measured** on the rendered page, not judged by eye. That is how
  the failing border was found.
- **The keyboard journey was walked** with real key presses: tab into the group, arrow keys to move
  and select, tab out to the next field.
- **Focus movement was asserted** at each step change and on each validation error.
- **The API was exercised directly**, including every failure path: malformed JSON, wrong types,
  over-long input, unknown answers, a five megabyte body, and a deleted guidance page.
- **The service was taken down mid-journey** to confirm the error message and that retrying resumed
  without re-entering anything.
- **`manage.py check --deploy`** passes clean with a real secret key.

## What I did not verify

- **No real screen reader pass.** Accessibility was checked against the accessibility tree and
  computed styles, not with VoiceOver or NVDA. This is the first thing I would do next.
- **The end-to-end journey test runs in jsdom, not a browser.** The browser checks were manual.
- **Outbound LEASE URLs were gathered by hand**, because the site returns 403 to automated requests.
  All but one were supplied directly; the fire safety section index is inferred from the confirmed
  pattern of its siblings and should be clicked before submission.
