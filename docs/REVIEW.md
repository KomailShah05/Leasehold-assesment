# Review

Part 3: a focused hardening pass over the existing build, then an honest look at it.

## Hardening pass

Six changes. Each fixed something that was actually wrong rather than adding polish, and each is
committed separately from the feature work.

**Keyword matching was a plain substring test.** `"bill"` matched inside `"billing"`, `"lift"`
inside `"shoplifting"`. The whole safety strategy is not routing someone confidently and wrongly,
so this was the weakest link. Words are now matched whole, with an optional plural or past tense,
because people write "charges" and "they charged me" rather than the dictionary form. Two existing
tests failed when this landed, showing the stricter matching had pushed some genuine matches below
the score floor. I fixed the keywords rather than lowering the floor, because the floor is the
safety margin.

**An over-sized request body escaped as an HTML error page.** Django's own limit fired before my
validation did, so a large body produced Django's HTML error rather than the JSON shape the client
understands, and in debug that page carries internal detail. Now caught and answered in our own
format.

**Production settings had no security headers.** `manage.py check --deploy` reported a list of
issues. Added HTTPS redirect, secure session and CSRF cookies, HSTS, `X_FRAME_OPTIONS = DENY`,
content-type nosniff, and a referrer policy so following a link out to LEASE does not leak the page
someone came from. The check now passes clean. Nothing is deployed, but leaving this undone means a
first deployment starts insecure by default.

**The free-text box could outlive the request.** It is the one place someone might type something
about their home, and browsers keep form history. Added `autoComplete="off"` and
`spellCheck={false}`. The hint now says plainly that we do not keep what they write, rather than
only warning them what not to type.

**The page title never changed.** The journey replaces content without changing the URL, so the
title said the same thing throughout. It now names the current question or result, which matters to
anyone using the title for orientation.

**`MINIMUM_SCORE` and `MINIMUM_LEAD` were defined twice**, in `services.py` and `classifier.py`. The
`services.py` copies were dead after scoring moved, but two constants sharing a name with no single
source of truth is what later drifts apart and changes behaviour quietly.

## Personal data and security

**What is collected: nothing.** No accounts, no contact fields, no analytics, no cookies for the
journey, no enquiry history. The free-text description is sent in a request body, used to pick a
category, and discarded. Nothing in the triage path writes a row, and a test asserts the database is
unchanged after a request.

**What I chose not to collect.** An email address to send results to, and any satisfaction
analytics. Both are obvious next features and both change the risk profile completely: an address
plus a description of a housing problem is personal data about someone's home, and this is a
prototype with no lawful basis established, no privacy notice and no retention policy.

**Retention, access, deletion.** Because nothing is stored there is nothing to retain, expose or
delete, which is the strongest position available and the reason to hold it. If enquiries were ever
stored I would want a decided retention period with automatic deletion rather than manual review;
the description treated as close to special category data, because housing problems reveal a lot
about a person; access limited to advisers who need it rather than all staff; and deletion on
request built in from the start.

**Free text is deliberately not logged.** It travels in a POST body, so it does not appear in access
logs the way a query parameter would. That is a reason to keep it in the body even though a GET
would be simpler to cache.

**Main risks, and where they stand.**

| Risk | Status |
| --- | --- |
| Markup injected through free text | Nothing typed is ever rendered; guidance comes from Wagtail and React escapes text. Covered by a test |
| Cross-origin abuse | Explicit `CORS_ALLOWED_ORIGINS` list from an environment variable, never allow-all |
| CSRF | The endpoint is `@csrf_exempt`: no cookies, no session, no stored state, so nothing to forge. First thing I would revisit if it ever wrote anything |
| Information leakage in errors | Fixed messages from a small set; a test asserts the error body has exactly two keys |
| Denial of service | **Not addressed.** No rate limiting on an unauthenticated endpoint. The gap I would close first for a real deployment |
| Content trust | Guidance comes from Wagtail, so a compromised editor account changes what people are told. An argument for review workflow on those pages |

## Accessibility

**Checks I ran.** Contrast measured on the rendered page rather than judged by eye; target sizes
measured against the 24x24 minimum; the keyboard journey walked with real key presses; focus
asserted after every step change and every validation error; the accessibility tree read to confirm
names and grouping; reflow checked at 375px.

**What I improved.**

- The choice border measured 2.08:1 against the page and needed 3:1 under WCAG 1.4.11. Darkened to
  3.51:1. It looked completely fine on screen and only failed once measured.
- The legal term inside each radio label produced an accessible name with no space, so a screen
  reader ran two phrases together as one word. Fixed with an explicit space.
- Focus now moves at exactly two moments: a step change, and a validation error. It is not taken on
  first load, where stealing it from the top of the page would be wrong.
- Field errors move focus and are therefore not `role="alert"`; the API error is `role="alert"` and
  does not take focus, because the person may be mid-sentence. Doing both announces twice.
- The page title names the current step.
- Added `prefers-reduced-motion` and Windows `forced-colors` handling, and a chosen option changes
  its whole row rather than relying on the small circle.

**What I would do next.**

1. **A real screen reader pass** with VoiceOver and NVDA. Everything above was verified against the
   accessibility tree and computed styles, which is not the same thing. This is the biggest gap.
2. **Test with someone who actually uses assistive technology**, which is worth more than any audit.
3. **Reconsider the first screen.** Seven options is a lot for someone who is stressed.
4. **A browser-level end-to-end test**, so the keyboard journey is checked automatically rather than
   by hand.

## Self code review

Reviewing this as if it were a colleague's pull request.

### What I would praise

- **`triage/classifier.py` and `services.py` are the right shape.** Pure functions, no Django
  imports, and the decision to refuse to answer expressed as three separately named reasons.
- **The classifier interface returns a route id and cannot return text.** That makes "we signpost,
  we do not advise" a structural property rather than a promise, and means a model-backed classifier
  could be dropped in without loosening it.
- **The tests were checked against reintroduced bugs.** Four separate mutations each failed the
  tests that should have caught them. A test that cannot fail is decoration.
- **`test_no_keyword_is_shared_between_routes` guards the taxonomy, not the code.** A shared word
  makes two routes tie, and ties go to the fallback, so a careless keyword would quietly make triage
  worse as it grew. That regression is invisible without this test.

### What I would question

- **Seven options on the first screen.** The weakest thing about the product. It grew from three,
  one reasonable-sounding addition at a time, and nobody re-asked whether the first decision was
  still easy. I would not add another.
- **`MINIMUM_SCORE = 2` and `MINIMUM_LEAD = 2` are unexplained numbers.** They are the entire safety
  margin between routing someone and giving up, and they were chosen by trying sample phrases. They
  deserve a corpus of realistic descriptions to tune against.
- **Keyword scoring is still crude.** Word-count weighting is a proxy for specificity, not
  specificity itself. It works on the phrasings I tried, which is exactly the bias a reviewer should
  distrust.
- **`ResultStep` renders both outcome and fallback.** Defensible, since they are deliberately framed
  alike, but it now has two shapes and a conditional heading with a comment explaining which one
  takes focus. That is a smell.
- **`content.py` is 300 lines of data in one file.** Fine now; the moment a seventh route appears it
  should be split or moved into the CMS.
- **`useTriage` returns nine values.** State, fetching, retry and restart in one hook. Still
  readable, but the file most likely to sprawl next.

### The abstraction a reviewer will challenge

`Classifier` is a Protocol with one implementation, which is usually a smell, and I would raise it
in someone else's PR. I kept it because it is not speculative generality: the interface returns a
route id and cannot return text, which is precisely what stops any future model-backed version
putting unapproved words in front of a person. It is about fifteen lines. If it had no safety
consequence I would have deleted it.

### Naming I am not happy with

- `match_route` returns a `RouteMatch` that may be `None`, and `chosen_by_person` means "the person
  picked this rather than us guessing" — which the API calls `inferred`. One word for one concept
  would be better.
- `guidance_key` alongside Wagtail's own `slug` on the same model is two names for overlapping ideas.
- `score_route` reads as though it scores a route, when it scores text against a route.

### Missing tests

- No test that a scenario cannot be paired with an answer id belonging to a different route. I
  believe it is handled; belief is not a test.
- No test for a guidance page deleted between the question and the answer.
- No frontend test for the timeout path end to end; the client behaviour is tested, not what the
  person sees.
- No test asserting a radio's accessible name includes its legal term. That bug happened once and
  nothing stops it happening again.
- No performance or load testing.

### What I would not merge yet

If this were going in front of real users rather than being a prototype:

1. **No rate limiting** on an unauthenticated endpoint.
2. **No real screen reader pass**, on a service whose users are described as often older and
   non-technical.
3. **One outbound URL is inferred rather than confirmed** — the fire safety section index. It
   follows the confirmed pattern of its siblings but has not been opened.
4. **The fallback links the LEASE home page** rather than a dedicated "get advice" page, despite
   being the destination for every query the app cannot place.

None of these are hard. All are the kind of thing that gets left until after launch, which is why I
would rather name them here.
