"""Tests for turning a request into a route, a question and an answer.

Also no Django. The classifier is injected, so these tests describe the rules
around classification without depending on how classification works.
"""

from triage import services
from triage.content import NOT_SURE_OPTION_ID


class AlwaysRepairs:
    """A classifier that is confident and wrong, to prove what overrides it."""

    def classify(self, text: str) -> str | None:
        return "repairs"


class NeverSure:
    def classify(self, text: str) -> str | None:
        return None


class Nonsense:
    """Returns a route id that does not exist."""

    def classify(self, text: str) -> str | None:
        return "not_a_real_route"


def test_a_chosen_scenario_is_used_as_given() -> None:
    match = services.match_route("repairs", None)

    assert match is not None
    assert match.route.id == "repairs"
    assert match.chosen_by_person is True


def test_a_chosen_scenario_overrides_the_classifier() -> None:
    """If someone has told us what their problem is about, nothing gets to
    second-guess them, including a model-backed classifier."""
    match = services.match_route("lease_extensions", "leaking roof", classifier=AlwaysRepairs())

    assert match is not None
    assert match.route.id == "lease_extensions"


def test_not_sure_goes_to_the_fallback() -> None:
    assert services.match_route(NOT_SURE_OPTION_ID, None) is None


def test_unknown_scenario_goes_to_the_fallback() -> None:
    assert services.match_route("parking_spaces", None) is None


def test_missing_input_goes_to_the_fallback() -> None:
    assert services.match_route(None, None) is None


def test_a_classifier_declining_goes_to_the_fallback() -> None:
    assert services.match_route(None, "anything", classifier=NeverSure()) is None


def test_a_classifier_naming_an_unknown_route_goes_to_the_fallback() -> None:
    """A future classifier must not be able to invent a route by returning a
    string we do not recognise."""
    assert services.match_route(None, "anything", classifier=Nonsense()) is None


def test_an_inferred_route_offers_a_way_to_say_we_got_it_wrong() -> None:
    match = services.match_route(None, "my service charge bill has gone up")

    assert match is not None
    assert match.chosen_by_person is False
    answer_ids = [answer.id for answer in services.question_for(match).answers]
    assert services.REJECT_ROUTE_ANSWER.id in answer_ids


def test_a_chosen_route_does_not_offer_that_option() -> None:
    """There is nothing to correct when the person chose the route themselves,
    and offering it would imply we had guessed."""
    match = services.match_route("service_charges", None)

    assert match is not None
    answer_ids = [answer.id for answer in services.question_for(match).answers]
    assert services.REJECT_ROUTE_ANSWER.id not in answer_ids


def test_every_i_am_not_sure_answer_leads_to_an_adviser() -> None:
    """Uncertainty inside a route must never resolve to a confident outcome."""
    from triage.content import ADVISER_GUIDANCE_KEY, ROUTES

    unsure = [
        answer
        for route in ROUTES
        for answer in route.question.answers
        if answer.id in {"unsure", "not_sure"}
    ]

    assert unsure, "expected an 'I am not sure' answer on the routes"
    assert all(answer.guidance_key == ADVISER_GUIDANCE_KEY for answer in unsure)


def test_an_answer_we_did_not_offer_is_rejected() -> None:
    match = services.match_route("repairs", None)

    assert match is not None
    assert services.resolve_answer(match, "banana") is None


def test_a_real_answer_resolves_to_its_guidance() -> None:
    match = services.match_route("repairs", None)

    assert match is not None
    answer = services.resolve_answer(match, "shared_area")
    assert answer is not None
    assert answer.guidance_key == "repairs-shared-areas"


def test_the_reject_answer_is_only_available_on_an_inferred_route() -> None:
    chosen = services.match_route("service_charges", None)
    inferred = services.match_route(None, "my service charge bill has gone up")

    assert chosen is not None and inferred is not None
    assert services.resolve_answer(chosen, services.REJECT_ROUTE_ANSWER.id) is None
    assert services.resolve_answer(inferred, services.REJECT_ROUTE_ANSWER.id) is not None
