# How AI was used

The brief asks for an honest account of what AI helped with, what I changed or rejected, and what
was verified. This is that account. It is written from the record of the working sessions rather
than reconstructed afterwards.

## The short version

I used Claude as a pair programmer throughout the build, one ticket at a time. I set the scope,
the architecture and the product decisions; it drafted code and copy against them, and I redirected
it when I disagreed. Every ticket was reviewed before it was committed, and several were sent back.

What it was **not** used for: writing the application in one pass, generating the guidance a user
reads, or making product decisions on my behalf.

## What it genuinely helped with

- **Drafting code to a decided design.** The triage rules, the API layer, the React components and
  the tests were AI-drafted against decisions I had already made in `PLAN.md`.
- **Finding bugs by exercising the code rather than reading it.** Three real defects surfaced this
  way, each of which would have survived a code review:
  - The escape-hatch answer ("this is not what my problem is about") returned an outcome still
    labelled with the route the person had just rejected. That is the fallback failing to fire,
    which is the single highest-risk failure in this application.
  - The legal term inside each radio label produced an accessible name with no space
    ("…bill or chargeService charges…"), so a screen reader ran two phrases together as one word.
    It looked perfect on screen.
  - The choice border measured 2.08:1 against the page, failing WCAG 1.4.11, which needs 3:1. It
    also looked fine.
- **Plain-English wording.** Draft copy was consistently reworded to remove legal vocabulary and to
  phrase every outcome as a possible next step.
- **Test cases I would not have thought of.** In particular the taxonomy guard that no keyword is
  shared between two routes, since a shared word makes routes tie and ties go to the fallback — a
  regression that would make triage quietly worse as it grew, with nothing visibly broken.

## What I changed or rejected

- **Ambiguity handling.** It proposed sending any ambiguous free text straight to the fallback. I
  rejected that in favour of taking the strongest match, asking the follow-up question, and falling
  back only if still unclear — which is what `PLAN.md` had said from the start.
- **Generating advice with a language model.** It was proposed that the fallback could produce an
  AI-written suggestion labelled as such. I decided against it: a model asked what someone should do
  about their lease will produce something that reads as legal advice, a worried person reads the
  answer rather than the disclaimer, and it would put an external service and free text that may
  contain personal details into the core flow. AI classification sits behind an interface that
  returns a route id and cannot return text; that boundary is the point.
- **Scraping LEASE's site for content.** Rejected. Their wording is copyrighted and is itself legal
  guidance; copying it in would turn signposting into advising. All summary copy here is original,
  and every link goes out to their page. (Their site also blocks automated access, so the URLs were
  gathered by hand.)
- **Scope.** It recommended staying at three routes. I chose to widen to six once real LEASE section
  URLs were available. `PLAN.md` records the change and the cost: a longer first screen, which is a
  harder first decision for the reader the brief describes.
- **Uncertainty routing.** Every "I am not sure" answer originally resolved to one shared adviser
  page. I wanted each to reach its own topic overview. That meant overriding a safety rule, so it
  was replaced rather than deleted: uncertainty must still never reach a confident specific outcome,
  and a test now checks every overview page still names an adviser.
- **Code style and structure.** I asked for arrow functions throughout, and for the journey to be
  composed from small shared components rather than large step files.
- **Dependencies.** I questioned using `fetch` rather than axios interceptors. We kept `fetch`:
  there is no auth or token refresh here, which is what interceptors mainly buy, and the typed
  client already gives one error shape. The missing piece axios would have provided — a request
  timeout — was added explicitly with `AbortSignal.timeout`.
- **Configuration.** A proposal to make the database configurable through an environment variable
  was declined as unnecessary for a prototype that is not being deployed.

## What was verified, and how

Verification was done by running things, not by assertion:

- **68 tests**, 54 backend and 14 frontend, all passing.
- **The tests were checked against deliberately broken code.** Reintroducing the escape-hatch bug
  failed one test; removing the ambiguity guard failed two. A test that cannot fail is decoration.
- **Contrast and target sizes were measured** on the rendered page, not judged by eye. That is how
  the failing border was found.
- **The keyboard journey was walked** with real key presses: tab into the group, arrow keys to move
  and select, tab out to the next field.
- **Focus movement was asserted** at each step change and on each validation error.
- **The API was exercised directly**, including every failure path: malformed JSON, wrong types,
  over-long input, unknown answers, and a deleted guidance page.
- **The service was taken down mid-journey** to confirm the error message and that retrying resumed
  without re-entering anything.

## What I did not verify

Stated plainly rather than left to be assumed:

- **No real screen reader pass.** Accessibility was checked against the accessibility tree and
  computed styles, not with VoiceOver or NVDA. This is the first thing I would do next.
- **The end-to-end journey test runs in jsdom, not a browser.** The real browser checks were manual.
- **Outbound LEASE URLs have not been opened by me from this environment**, because the site returns
  403 to automated requests. They were supplied by hand and are correct as far as I can confirm.
