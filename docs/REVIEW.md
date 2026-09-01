# Part 3 — hardening and review

A focused quality pass over the existing build, then an honest look at it.

## What I changed

Six changes, each fixing something actually wrong rather than adding polish.

**Keyword matching was a plain substring test.** `"bill"` matched inside `"billing"`, `"lift"`
inside `"shoplifting"`. Since the whole safety strategy is *do not route someone confidently and
wrongly*, that was the weakest link in the classifier. Words are now matched whole, with an
optional plural or past tense so `"charges"` and `"they charged me"` still match — people write
those, not the dictionary form. Two of my own tests failed when I made the change, which showed the
strictness had lowered some genuine scores below the threshold; I fixed the keywords rather than
lowering the threshold, since the threshold is the safety margin.

**`MINIMUM_SCORE` and `MINIMUM_LEAD` were defined twice**, in `services.py` and `classifier.py`.
The `services.py` copies were dead after scoring moved, but two constants with the same name and no
single source of truth is exactly the sort of thing that later drifts apart and changes behaviour
silently. Removed.

**An over-sized request body escaped as an HTML error page.** Django's own limit fired before my
validation did, so a large body produced Django's HTML error rather than the JSON shape the client
understands — and in debug that page carries internal detail. The client fell through to "we
received an unexpected response", which tells the person nothing useful. Now caught and answered in
our own format, with a test.

**Production settings had no security headers at all.** `manage.py check --deploy` flagged a list of
issues. Added HTTPS redirect, secure session and CSRF cookies, HSTS for a year with subdomains and
preload, `X_FRAME_OPTIONS = "DENY"`, content-type nosniff, and a referrer policy so following a link
out to LEASE does not leak the page someone came from. The check now passes clean. The prototype is
not deployed, but leaving this undone means the first real deployment starts insecure by default.

**The free-text box could outlive the request.** It is the one place someone might type something
about their home, and browsers keep form history. Added `autoComplete="off"` and `spellCheck={false}`
so the text is not stored in form history or checked against a personal dictionary. The hint now
also says plainly that we do not keep what they write, rather than only telling them what not to
type.

**The page title never changed.** The journey replaces the content without changing the URL, so the
title said "Leasehold enquiry triage" throughout. It now names the current question or result. This
matters most to people who use the title for orientation — screen reader users often hear it when
returning to a tab, and it is what browser history and tab switching show.

**Five tests were added**, including one I should have written earlier: that nothing a person types
is ever echoed back in a response. Everything shown comes from editor-written guidance, so free text
has no route to the screen; that test holds the door closed, because a future change that reflected
input would be the first place markup could be injected.

## Personal data and security

**What is collected: nothing.** No accounts, no contact fields, no analytics, no cookies for the
journey, no enquiry history. The free-text description is sent in a request body, used to pick a
category, and discarded. Nothing in the triage path writes a row, and a test asserts the database is
unchanged after a request.

**What I chose not to collect.** An email address to send results to, and any "how did we do"
analytics. Both are the obvious next features and both would change the risk profile completely: an
address plus a description of a housing problem is personal data about someone's home, and this is a
prototype with no lawful basis established, no privacy notice and no retention policy.

**Retention, access, deletion.** Because nothing is stored, there is nothing to retain, expose or
delete — which is the strongest position available and the reason to hold it. If enquiries were ever
stored I would want: a decided retention period with automatic deletion rather than manual review,
the description treated as special-category-adjacent because housing problems reveal a lot about a
person, access limited to advisers who need it rather than all staff, and deletion on request built
in from the start rather than added later.

**Free text is deliberately not logged.** It travels in a POST body, so it does not appear in access
logs the way a query parameter would. That is a reason to keep it in the body even though a GET
would be simpler to cache.

**Main risks, and where they stand.**

- *Injection of markup through free text.* Nothing typed is ever rendered — the summary comes from
  Wagtail and React escapes text by default. Now covered by a test.
- *Cross-origin abuse.* `CORS_ALLOWED_ORIGINS` is an explicit list from an environment variable,
  never `CORS_ALLOW_ALL_ORIGINS`.
- *CSRF.* The triage endpoint is `@csrf_exempt`. It has no cookies, no session and no stored state,
  so there is no cross-site request worth forging. I am comfortable defending that, but it is the
  first thing I would revisit if the endpoint ever wrote anything.
- *Information leakage in errors.* Every error returns a fixed message from a small set; nothing
  reflects internal detail, and a test asserts the error body has exactly two keys.
- *Denial of service.* Not addressed. There is no rate limiting, and the endpoint is unauthenticated.
  For a real deployment this is the gap I would close first.
- *Content trust.* Guidance comes from Wagtail, so a compromised editor account could change what
  people are told. That is a real risk in the production system and an argument for review workflow
  on those pages.

## Accessibility

**Checks I ran.** Contrast measured on the rendered page rather than judged by eye; target sizes
measured against the 24x24 minimum; the keyboard journey walked with real key presses (tab into the
group, arrow keys to move and select, tab out); focus asserted after every step change and every
validation error; the accessibility tree read to confirm names and grouping; reflow checked at
375px; and an automated test that focus actually lands on the error message.

**What I improved.**

- The choice border measured 2.08:1 against the page and needed 3:1 (1.4.11). Darkened to 3.51:1.
  It looked completely fine on screen and only failed once measured.
- The legal term inside each radio label produced an accessible name with no space, so a screen
  reader ran two phrases together as one word. Fixed by rendering an explicit space.
- Focus is now moved deliberately at exactly two moments: a step change, and a validation error. It
  is not taken on first load, where stealing it from the top of the page would be wrong.
- Field errors move focus and are therefore not `role="alert"`; the API error is `role="alert"` and
  does not take focus, because the person may be mid-sentence. Doing both announces twice.
- The page title now names the current step.
- Added `prefers-reduced-motion` and Windows `forced-colors` handling, and a chosen option changes
  its whole row rather than relying on the small circle.

**What I would do next.**

1. **A real screen reader pass** with VoiceOver and NVDA. Everything above was verified against the
   accessibility tree and computed styles, which is not the same thing. This is the single biggest
   gap.
2. **Test with a real person** who uses assistive technology, which is worth more than any audit.
3. **Reconsider the first screen.** Seven options is a lot for someone who is stressed. Grouping, or
   leading with the free-text box, would probably serve people better than the current list.
4. **A browser-level end-to-end test** so the keyboard journey is checked automatically rather than
   by hand.

## Self code review

Reviewing this as if it were a colleague's PR.

### What I would praise

- **`triage/classifier.py` and `triage/services.py` are the right shape.** Pure functions, no Django
  imports, and the decision to refuse to answer expressed as three separate named reasons. The
  taxonomy is short enough to read in one sitting.
- **The classifier interface returns a route id and cannot return text.** That is what makes "we
  signpost, we do not advise" a structural guarantee rather than a promise, and it means a
  model-backed classifier could be dropped in without loosening it.
- **The tests were checked against reintroduced bugs.** Three separate mutations each failed the
  tests that should have caught them.
- **`test_no_keyword_is_shared_between_routes` guards the taxonomy, not the code.** That class of
  regression is invisible without it.

### What I would question

- **Seven options on the first screen.** This is the weakest thing about the product. It grew from
  three, one reasonable-sounding addition at a time, and nobody re-asked whether the first decision
  was still easy. It is not obviously wrong, but I would want it justified in review.
- **`MINIMUM_SCORE = 2` and `MINIMUM_LEAD = 2` are unexplained magic numbers.** They are the entire
  safety margin between routing someone and giving up, and they were chosen by trying sample
  phrases. They deserve either a comment showing the working or a small corpus of realistic
  descriptions to tune against.
- **Keyword scoring is crude.** Word-count weighting is a proxy for specificity, not specificity
  itself. Substring matching means "charge" matches inside other words. It works on the phrasings I
  tried, which is exactly the bias a reviewer should distrust.
- **`ResultStep` renders both outcome and fallback.** Defensible, since they are deliberately framed
  alike, but the component now has two shapes and a conditional heading with a comment explaining
  which one takes focus. That is a smell.
- **`content.py` is 300 lines of data in one file.** Fine now; the moment a seventh route appears it
  should be split or moved into the CMS.
- **`useTriage` returns nine values.** It is doing state, fetching, retry and restart. Still readable,
  but it is the file most likely to sprawl next.

### Naming I am not happy with

- `match_route` returns a `RouteMatch` that may be `None`, and `chosen_by_person` is really "the
  person picked this rather than us guessing". `inferred` is used for the same idea in the API. One
  word for one concept would be better.
- `guidance_key` versus `slug` versus Wagtail's own `slug` on the same model is three names for
  overlapping ideas.
- `question_for` and `resolve_answer` read fine; `score_route` reads like it scores a route rather
  than scoring text against a route.

### Missing tests

- **No test that a chosen scenario cannot be smuggled past validation** by sending both a scenario
  and a contradicting answer id from a different route. I believe it is handled, but belief is not a
  test.
- **No test for concurrent editing of guidance** — an editor unpublishing mid-journey is covered,
  deleting between question and answer is not.
- **No frontend test for the timeout path** end to end; the client behaviour is tested but not what
  the person sees.
- **No test asserting the accessible name of a radio includes its legal term.** That bug happened
  once and nothing stops it happening again.
- **No performance or load testing at all.**

### What I would not merge yet

If this were going in front of real users rather than being a prototype:

1. **No rate limiting** on an unauthenticated endpoint.
2. **No real screen reader pass**, on a service whose users are explicitly described as often older
   and non-technical.
3. **One outbound URL is inferred rather than confirmed** — the fire safety section index,
   `/building-management/fire-safety/`. It follows the confirmed pattern of its siblings but has not
   been opened. Every other link was supplied directly. A 404 at that moment is a bad failure for a
   worried person.
4. **The fallback links the LEASE home page** rather than a dedicated "get advice" page, despite
   being the destination for every query the app cannot place. It is now the only page in the app
   still pointing there.

None of those are hard. All of them are the kind of thing that gets left until after launch, which
is why I would rather name them here.


## A note on two things a reviewer will question

**Six routes.** The plan said three. I widened it once real LEASE URLs were available, and the cost
is a seven-option first screen for a reader the brief describes as often stressed and non-technical.
I would not add a seventh. If I were starting again I would either hold at three or group them.

**The `Classifier` interface has one implementation.** That is usually a smell, and I would push
back on it in someone else's PR. I kept it because it is not speculative generality: the interface
returns a route id and cannot return text, which is what makes "we signpost, we do not advise" a
structural property rather than a promise about future good behaviour. It is about fifteen lines,
and it is the reason the answer to "would you use AI here?" can be "yes, for classification, behind
a boundary that cannot reach the screen". If it had no safety consequence I would have deleted it.
