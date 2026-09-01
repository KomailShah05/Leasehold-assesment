"""Tests for deciding which route a description belongs to.

No Django here: the classifier is deliberately importable without a database
or a settings module, and these tests prove it stays that way.

The most important tests in this file are the ones asserting that we return
None. A wrong route sends someone who is already worried down a path that does
not fit their problem, which is worse than admitting we could not tell.
"""

import pytest

from triage.classifier import MINIMUM_LEAD, KeywordClassifier, score_route
from triage.content import ROUTES, ROUTES_BY_ID

classifier = KeywordClassifier()


@pytest.mark.parametrize(
    ("description", "expected"),
    [
        ("my service charge bill has gone up a lot this year", "service_charges"),
        ("I cannot afford the service charge bill", "service_charges"),
        ("I want to extend my lease, only 70 years left", "lease_extensions"),
        ("there is damp and mould and it has not been fixed", "repairs"),
        ("water is leaking into my flat from upstairs", "repairs"),
        ("the managing agent is ignoring me", "management_problems"),
        ("we want to set up right to manage", "right_to_manage"),
        ("I am worried about the cladding and fire safety", "fire_safety"),
    ],
)
def test_matches_each_route(description: str, expected: str) -> None:
    assert classifier.classify(description) == expected


@pytest.mark.parametrize(
    "description",
    [
        "",
        "   ",
        "hello",
        "my neighbour plays loud music at night",
        "I want to sell my car",
    ],
)
def test_declines_when_nothing_matches(description: str) -> None:
    assert classifier.classify(description) is None


def test_declines_when_the_words_fit_two_routes() -> None:
    """The highest-risk case: ambiguity must not be resolved by guessing.

    "the lift is broken and they charged me for it" is genuinely both a repair
    and a charge. Picking the higher score would be a confident wrong answer.
    """
    description = "the lift is broken and they charged me for it"

    scores = {route.id: score_route(description, route) for route in ROUTES}
    matched = [route_id for route_id, score in scores.items() if score > 0]

    assert len(matched) > 1, "this description should touch more than one route"
    assert classifier.classify(description) is None


def test_declines_when_the_lead_is_too_small() -> None:
    """A near tie is still a tie for our purposes."""
    repairs = ROUTES_BY_ID["repairs"]
    service_charges = ROUTES_BY_ID["service_charges"]
    description = "there is a leak and I got a bill"

    lead = abs(score_route(description, repairs) - score_route(description, service_charges))

    assert lead < MINIMUM_LEAD
    assert classifier.classify(description) is None


def test_declines_on_a_single_weak_keyword() -> None:
    """One common word is a coincidence, not evidence."""
    assert score_route("I got a bill", ROUTES_BY_ID["service_charges"]) > 0
    assert classifier.classify("I got a bill") is None


def test_longer_phrases_count_for_more_than_single_words() -> None:
    """ "lease extension" is evidence; "lease" on its own is not."""
    route = ROUTES_BY_ID["lease_extensions"]

    assert score_route("lease extension", route) > score_route("freehold", route)


def test_matching_ignores_case_and_spacing() -> None:
    assert classifier.classify("  MY   SERVICE   CHARGE   Bill  ") == "service_charges"


def test_no_keyword_is_shared_between_routes() -> None:
    """A shared keyword would make two routes tie, sending good input to the
    fallback. This guards the taxonomy as more routes get added."""
    seen: dict[str, list[str]] = {}
    for route in ROUTES:
        for keyword in route.keywords:
            seen.setdefault(keyword, []).append(route.id)

    shared = {keyword: routes for keyword, routes in seen.items() if len(routes) > 1}

    assert shared == {}
