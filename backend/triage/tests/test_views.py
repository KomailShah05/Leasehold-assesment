"""Tests for the HTTP layer.

These need the database, because guidance wording lives in Wagtail. They check
the shape of each response and, more importantly, that the awkward cases end in
a usable answer rather than an error page.
"""

import json
from typing import Any

import pytest
from django.core.management import call_command
from django.test import Client
from django.urls import reverse

from guidance.models import GuidancePage


@pytest.fixture
def guidance(db: None) -> None:
    """The sample guidance, created the same way a developer would create it."""
    call_command("seed_guidance", verbosity=0)


def post(client: Client, **payload: Any) -> Any:
    response = client.post(
        reverse("triage"), data=json.dumps(payload), content_type="application/json"
    )
    return response, json.loads(response.content)


def test_routes_are_offered_with_the_not_sure_option(client: Client) -> None:
    """ "I am not sure" belongs in the same group as the real scenarios, so the
    API returns it alongside them rather than leaving it to the UI."""
    body = json.loads(client.get(reverse("triage-routes")).content)

    assert len(body["routes"]) >= 3
    assert body["notSureOption"]["id"] == "not_sure"
    assert all({"id", "label", "legalTerm"} <= route.keys() for route in body["routes"])


def test_choosing_a_scenario_returns_its_question(client: Client, guidance: None) -> None:
    response, body = post(client, scenario="repairs")

    assert response.status_code == 200
    assert body["status"] == "question"
    assert body["inferred"] is False
    assert body["question"]["answers"]


def test_describing_a_problem_returns_a_question_marked_as_inferred(
    client: Client, guidance: None
) -> None:
    response, body = post(client, description="my service charge bill has gone up a lot")

    assert body["status"] == "question"
    assert body["inferred"] is True
    answer_ids = [answer["id"] for answer in body["question"]["answers"]]
    assert "not_my_problem" in answer_ids


def test_answering_returns_an_outcome_with_guidance(client: Client, guidance: None) -> None:
    response, body = post(client, scenario="repairs", answerId="shared_area")

    assert body["status"] == "outcome"
    assert body["guidance"]["title"]
    assert body["guidance"]["leaseUrl"].startswith("https://www.lease-advice.org/")


@pytest.mark.parametrize(
    "payload",
    [
        {"scenario": "not_sure"},
        {"scenario": "something_we_do_not_cover"},
        {"description": "my neighbour plays loud music at night"},
        {"description": "the lift is broken and they charged me for it"},
    ],
)
def test_uncertainty_ends_in_the_fallback(
    client: Client, guidance: None, payload: dict[str, str]
) -> None:
    """Every way of not knowing leads to the same honest answer, not a guess."""
    response, body = post(client, **payload)

    assert response.status_code == 200
    assert body["status"] == "fallback"
    assert body["guidance"]["title"]


def test_saying_we_got_the_route_wrong_returns_the_fallback(client: Client, guidance: None) -> None:
    """Regression test. This once returned an outcome still labelled with the
    route the person had just rejected, which is the fallback failing to fire."""
    response, body = post(
        client, description="my service charge bill has gone up", answerId="not_my_problem"
    )

    assert body["status"] == "fallback"
    assert "route" not in body


def test_missing_guidance_falls_back_rather_than_erroring(client: Client, guidance: None) -> None:
    """An editor unpublishing a page must not turn into a server error for
    someone midway through the journey."""
    GuidancePage.objects.filter(guidance_key="repairs-shared-areas").delete()

    response, body = post(client, scenario="repairs", answerId="shared_area")

    assert response.status_code == 200
    assert body["status"] == "fallback"


@pytest.mark.parametrize(
    ("payload", "reason"),
    [
        ({}, "nothing given at all"),
        ({"description": "   "}, "only whitespace"),
        ({"description": 123}, "wrong type"),
        ({"scenario": ["repairs"]}, "wrong type"),
        ({"description": "a" * 2001}, "too long"),
        ({"scenario": "repairs", "answerId": "banana"}, "an answer we did not offer"),
    ],
)
def test_bad_input_is_refused_kindly(
    client: Client, guidance: None, payload: dict[str, Any], reason: str
) -> None:
    response, body = post(client, **payload)

    assert response.status_code == 400, reason
    assert body["status"] == "error"
    assert body["message"]


def test_unreadable_json_is_refused(client: Client, guidance: None) -> None:
    response = client.post(reverse("triage"), data="{oops", content_type="application/json")

    assert response.status_code == 400
    assert json.loads(response.content)["message"]


def test_errors_never_leak_internal_detail(client: Client, guidance: None) -> None:
    """Someone poking at the API should learn nothing about how it is built."""
    response, body = post(client, scenario="repairs", answerId="banana")

    assert set(body) == {"status", "message"}
    assert "Traceback" not in body["message"]


def test_the_endpoint_only_accepts_post(client: Client) -> None:
    assert client.get(reverse("triage")).status_code == 405


def test_every_route_can_be_completed(client: Client, guidance: None) -> None:
    """Walks every answer of every route through to an outcome, so a route
    added without its guidance page cannot pass unnoticed."""
    from triage.content import ROUTES

    for route in ROUTES:
        for answer in route.question.answers:
            response, body = post(client, scenario=route.id, answerId=answer.id)
            assert response.status_code == 200, f"{route.id}/{answer.id}"
            assert body["status"] in {"outcome", "fallback"}, f"{route.id}/{answer.id}"
            assert body["guidance"] is not None, f"{route.id}/{answer.id} has no guidance"
