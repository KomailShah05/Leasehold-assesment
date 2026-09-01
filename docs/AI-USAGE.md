# AI usage

An honest summary of how I used AI during the assessment, what I changed or rejected, and what I
verified myself.

## How I used it

I defined the architecture and acceptance criteria for each ticket, then used Claude as a coding
pair to help implement them one task at a time. I reviewed the output before committing each change,
and the Git history reflects that process.

I did not use AI to generate the application in one pass, make product decisions, or write the
guidance shown to users.

## Where it helped

AI mainly helped me with implementation, test ideas and reviewing edge cases.

It helped uncover four real issues:

* The "this is not my problem" answer could still return an outcome for the rejected route.
* Screen-reader text in radio labels was missing a space between the label and legal term.
* The choice border failed the WCAG 1.4.11 contrast requirement.
* Keyword matching used substring matching, so `bill` could match inside `billing`.

It also helped identify useful regression tests, including checking that keywords are not shared
between routes.

I reviewed the user-facing copy myself and changed wording that was too legalistic or could be
interpreted as advice.

## What I changed or rejected

I rejected several suggestions where they did not fit the problem:

* **AI-generated advice:** rejected because this is a legal-adjacent service. The classifier can
  return only a route ID, never user-facing text.
* **Ambiguous text to immediate fallback:** rejected. Where there is a clear enough match, the
  prototype asks a follow-up question and only falls back when it still cannot be confident.
* **Scraping LEASE content:** rejected. Guidance is original and links to LEASE's authoritative
  pages instead.
* **More routes:** I kept the scope deliberately small, although it grew from three to six once
  suitable LEASE sections were identified.
* **Extra dependencies:** kept `fetch` instead of adding axios because the prototype has no
  authentication or token-refresh requirement. A request timeout was added explicitly instead.

## What I verified

I verified the application by running the code rather than relying on AI output:

* 79 tests — 65 backend and 14 frontend — passing through `./scripts/test.sh`.
* Tests were checked against deliberately broken code to confirm they actually caught the
  regressions.
* Keyboard navigation, focus movement and validation behaviour were tested.
* Contrast and target sizes were measured on the rendered page.
* API failure cases were tested, including malformed JSON, invalid types, oversized input, unknown
  answers and missing guidance.
* The service was taken offline during a journey to verify the retry behaviour.
* `manage.py check --deploy` passes with a real secret key.

## What I did not verify

* I did not complete a real screen-reader test with VoiceOver or NVDA. I checked the accessibility
  tree and computed styles instead.
* The end-to-end journey test runs in jsdom; browser behaviour was checked manually.
* LEASE URLs were gathered manually because the site returns 403 to automated requests. One
  fire-safety URL is still inferred from the confirmed URL pattern and should be checked manually
  before submission.

The final implementation is my responsibility. I reviewed, tested and changed the AI-generated
suggestions before they were committed.
