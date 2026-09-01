"""Deciding which route a description belongs to.

This is the one part of triage a language model could plausibly do better, so
it sits behind a small interface of its own. Everything else — the questions,
the guidance wording, the fallback — stays deterministic regardless of what
implements ``Classifier``.

The boundary is drawn deliberately narrow. A classifier returns a route id or
None. It cannot write text, so no implementation of this interface, model-backed
or otherwise, can put words in front of a person that an editor did not approve.
That is what keeps "we signpost, we do not advise" true no matter what is
plugged in here.
"""

import re
from functools import cache
from typing import Protocol

from triage.content import ROUTES, Route

# Free text has to clear this before we will name a route at all. One bare
# keyword ("bill") is a coincidence; we want a little more than that.
MINIMUM_SCORE = 2

# How far ahead the best route must be before we treat it as the answer. A tie,
# or a near tie, means the words genuinely fit two topics, and picking one would
# be a guess wearing a confident face.
MINIMUM_LEAD = 2


class Classifier(Protocol):
    """Turns a description into a route id, or None when not confident.

    Returning None is a real answer, not a failure: it sends the person to the
    fallback and a human adviser. Any implementation must be willing to give it.
    """

    def classify(self, text: str) -> str | None: ...


def normalise(text: str) -> str:
    """Lower-case and collapse whitespace, so matching is not tripped by typing."""
    return " ".join(text.lower().split())


@cache
def _pattern(keyword: str) -> re.Pattern[str]:
    """Match a keyword as whole words, allowing a plural.

    Plain substring matching was too loose: "bill" matched inside "billing",
    which is a different subject. Requiring word boundaries fixes that, but
    boundaries alone are too strict: people write "charges" and "they charged
    me", not the dictionary form. Allowing a plural or a past tense keeps those
    and still refuses "billing".
    """
    return re.compile(rf"\b{re.escape(keyword)}(?:s|es|d|ed)?\b")


def matches(keyword: str, normalised_text: str) -> bool:
    return _pattern(keyword).search(normalised_text) is not None


def score_route(text: str, route: Route) -> int:
    """How strongly a description points at one route.

    Longer keyword phrases count for more than single words, because "lease
    extension" is real evidence and "lease" on its own is not: almost every
    person using this service will write the word "lease" at some point.
    """
    normalised = normalise(text)
    return sum(len(keyword.split()) for keyword in route.keywords if matches(keyword, normalised))


class KeywordClassifier:
    """The deterministic rules that ship today.

    Chosen over a model for the core flow because it is reproducible, testable
    without a network, cannot hallucinate, and cannot fail because a third party
    is having a bad afternoon.
    """

    def classify(self, text: str) -> str | None:
        if not text.strip():
            return None

        scores = sorted(
            ((route, score_route(text, route)) for route in ROUTES),
            key=lambda pair: pair[1],
            reverse=True,
        )

        best_route, best_score = scores[0]
        runner_up_score = scores[1][1] if len(scores) > 1 else 0

        # Three separate reasons to decline, all of which lead to the fallback:
        # nothing matched, the best match was too weak to trust, or two routes
        # were close enough that choosing between them would be a guess.
        if best_score < MINIMUM_SCORE:
            return None
        if best_score - runner_up_score < MINIMUM_LEAD:
            return None
        return best_route.id


DEFAULT_CLASSIFIER: Classifier = KeywordClassifier()
