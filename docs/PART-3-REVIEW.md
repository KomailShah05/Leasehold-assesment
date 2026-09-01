# Part 3 — Hardening and review

A focused hardening pass over the existing build, followed by an honest review of the result.

## Hardening pass

I made six changes, each addressing a real issue rather than adding polish.

* **Improved keyword matching.** Matching was originally based on simple substrings, so words such
  as `bill` could match `billing`. Matching now uses whole words with basic plural/past-tense
  handling. I kept the existing score threshold rather than lowering it when two tests exposed
  weaker matches.
* **Handled oversized requests.** A very large request could bypass our validation and return
  Django's HTML error page. It now returns the same JSON error shape as other invalid requests.
* **Hardened production settings.** Added HTTPS redirect, secure cookies, HSTS, clickjacking
  protection, content-type protection and a referrer policy. `manage.py check --deploy` now passes
  cleanly.
* **Reduced browser retention of free text.** The description field now uses `autocomplete="off"`
  and `spellCheck={false}`, and the UI makes it clear that the text is not stored.
* **Improved page titles.** The document title now reflects the current question or result, helping
  users understand where they are.
* **Removed duplicated constants.** `MINIMUM_SCORE` and `MINIMUM_LEAD` were defined in two places.
  The unused copies were removed so there is one source of truth.

## Personal data and security

**Nothing is stored.** There are no accounts, contact fields, analytics or enquiry history. Free text
is sent only with the request, used for triage and then discarded.

I deliberately did not collect email addresses or other contact details. If enquiries were stored in
a future version, I would define retention and deletion rules first, restrict access to staff who
need it, and avoid retaining more information than necessary.

Free text is kept in the POST body and is never echoed back or logged by the application.

| Risk            | Current approach                                                        |
| --------------- | ----------------------------------------------------------------------- |
| Input injection | User text is never rendered back to the page                            |
| CORS            | Explicit allowed-origin list                                            |
| CSRF            | Endpoint is stateless and does not use cookies or sessions              |
| Error leakage   | Fixed user-facing error messages                                        |
| DoS             | **Not addressed** — rate limiting would be a priority before production |
| Content changes | Guidance is editor-managed in Wagtail                                   |

## Accessibility

I checked:

* Keyboard navigation and radio-group behaviour
* Focus movement after errors and step changes
* Accessibility tree and accessible names
* Colour contrast and target sizes
* Reflow at 375px
* Reduced-motion and forced-colour behaviour

The hardening pass fixed a contrast issue with the choice border and an accessible-name issue where
the legal term ran directly into the label text.

Focus is moved deliberately after step changes and validation errors rather than on every render.

### What I would do next

1. Test with VoiceOver and NVDA.
2. Test the journey with people who use assistive technology.
3. Revisit the first screen because seven choices may be too much for someone who is stressed.
4. Add a browser-level end-to-end test for the complete keyboard journey.

## Self code review

### What I like

* The triage rules are isolated from Django and easy to test.
* Routing and editorial content are separated.
* The classifier can only return a route ID, not user-facing text.
* Tests cover important failure and ambiguity cases rather than only happy paths.
* The fallback behaviour is explicit and deliberately conservative.

### What I would question

* **Seven options on the first screen.** This is the main product concern. I would not add more
  without user research.
* **`MINIMUM_SCORE` and `MINIMUM_LEAD`.** These thresholds work for the current examples but should
  eventually be tuned against a larger set of realistic user descriptions.
* **Keyword scoring.** It is intentionally simple, but it is still only a proxy for understanding
  someone's situation.
* **`Classifier` abstraction.** There is currently one implementation, so this could be seen as
  unnecessary abstraction. I kept it because it provides a safety boundary: a future classifier can
  return a route ID but cannot generate guidance text.
* **`useTriage` and `content.py`.** Both are still manageable, but would be the first places I would
  consider splitting if the prototype grew.

### Missing tests

* Reject an answer ID that belongs to a different route.
* Verify the accessible name of a radio includes its legal term.
* Test the timeout behaviour through the user interface.
* Add browser-level coverage for the complete journey.

### What I would not merge for production

Before real users could rely on this service, I would address:

1. Rate limiting on the unauthenticated endpoint.
2. A real screen-reader and assistive-technology test.
3. Verification of the remaining inferred LEASE URL.
4. A more specific adviser destination instead of the general LEASE homepage for the fallback.

These are deliberately left as known gaps rather than hidden behind the prototype's polish.
