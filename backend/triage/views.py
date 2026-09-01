"""HTTP layer for triage. Validate, call the rules, return JSON.

There is deliberately no decision-making here. Which route someone lands on is
decided in ``triage.services``; this module only parses a request, looks up the
guidance wording in Wagtail, and shapes the response.

Responses use a status of "question", "outcome" or "fallback". Clients switch
on that one field rather than checking whether other fields happen to be null.
"""

import json

from django.core.exceptions import RequestDataTooBig
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from guidance.models import GuidancePage
from triage import services
from triage.content import (
    FALLBACK_GUIDANCE_KEY,
    FALLBACK_MESSAGE,
    FALLBACK_TITLE,
    NOT_SURE_OPTION_ID,
    NOT_SURE_OPTION_LABEL,
    ROUTES,
    Route,
)

# Someone describing a problem needs room, but not unlimited room. This is
# generous for a few sentences and small enough that we are not parsing an
# essay we would only ever keyword-match.
MAX_DESCRIPTION_LENGTH = 2000


def _route_payload(route: Route) -> dict[str, str]:
    return {"id": route.id, "label": route.label, "legalTerm": route.legal_term}


def _guidance_payload(guidance_key: str) -> dict[str, str] | None:
    page = GuidancePage.objects.live().filter(guidance_key=guidance_key).first()
    if page is None:
        return None
    return {"title": page.title, "summary": page.summary, "leaseUrl": page.lease_url}


def _fallback_response() -> JsonResponse:
    """The safe answer: say we could not place it, and offer a person.

    If even the adviser page is missing we still return a usable fallback
    rather than an error, because this is the response someone sees when
    things have already not gone to plan.
    """
    return JsonResponse(
        {
            "status": "fallback",
            "title": FALLBACK_TITLE,
            "message": FALLBACK_MESSAGE,
            "guidance": _guidance_payload(FALLBACK_GUIDANCE_KEY),
        }
    )


def _error(message: str, status: int = 400) -> JsonResponse:
    """One error shape, and never any internal detail."""
    return JsonResponse({"status": "error", "message": message}, status=status)


@require_http_methods(["GET"])
def routes(request: HttpRequest) -> HttpResponse:
    """The scenario options, so the React app never hardcodes the wording.

    "I am not sure" is returned as part of the same list, because it belongs in
    the same radio group as the real scenarios rather than off to one side.
    """
    return JsonResponse(
        {
            "routes": [_route_payload(route) for route in ROUTES],
            "notSureOption": {"id": NOT_SURE_OPTION_ID, "label": NOT_SURE_OPTION_LABEL},
        }
    )


# No cookies, no session and no stored state are involved in this endpoint, so
# there is no cross-site request to forge. Exempting it keeps the React app from
# needing a CSRF token for what is effectively a stateless calculation.
@csrf_exempt
@require_http_methods(["POST"])
def triage(request: HttpRequest) -> HttpResponse:
    try:
        payload = json.loads(request.body)
    except RequestDataTooBig:
        # Reading an over-sized body otherwise escapes as Django's own HTML
        # error page, which is the wrong shape for the client and, in debug,
        # carries internal detail. Answer in our own format instead.
        return _error("Please describe the problem in a little less detail.")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _error("We could not read that request.")

    if not isinstance(payload, dict):
        return _error("We could not read that request.")

    scenario = payload.get("scenario")
    description = payload.get("description")
    answer_id = payload.get("answerId")

    fields = ((scenario, "scenario"), (description, "description"), (answer_id, "answerId"))
    for value, name in fields:
        if value is not None and not isinstance(value, str):
            return _error(f"The {name} field must be text.")

    if description is not None and len(description) > MAX_DESCRIPTION_LENGTH:
        return _error("Please describe the problem in a little less detail.")

    if scenario is None and not (description or "").strip():
        return _error("Please choose an option or describe the problem.")

    match = services.match_route(scenario, description)
    if match is None:
        return _fallback_response()

    if answer_id is None:
        question = services.question_for(match)
        return JsonResponse(
            {
                "status": "question",
                "route": _route_payload(match.route),
                "inferred": not match.chosen_by_person,
                "question": {
                    "id": question.id,
                    "text": question.text,
                    "answers": [
                        {"id": answer.id, "label": answer.label} for answer in question.answers
                    ],
                },
            }
        )

    answer = services.resolve_answer(match, answer_id)
    if answer is None:
        return _error("Please choose one of the options shown.")

    if answer.id == services.REJECT_ROUTE_ANSWER.id:
        # They have told us the route we guessed is wrong. Showing an outcome
        # still labelled with that route would be worse than admitting we could
        # not place the problem.
        return _fallback_response()

    guidance = _guidance_payload(answer.guidance_key)
    if guidance is None:
        # The route was right but its guidance page is missing or unpublished.
        # Falling back is better than showing an outcome with no next step.
        return _fallback_response()

    return JsonResponse(
        {
            "status": "outcome",
            "route": _route_payload(match.route),
            "guidance": guidance,
        }
    )
