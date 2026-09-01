"""The triage rules.

Deterministic, and deliberately so. A person in difficulty needs an answer we
can explain, reproduce and test; a model that is usually right is worse here
than a rule that is always the same. There is no external API call in this
path, so the journey cannot fail because a third party is down.

Picking a category is the one part that could sensibly be done by a model, so
it lives behind the ``Classifier`` interface in ``triage.classifier``. What is
asked, what is shown and when we give up are decided here and stay fixed.

Pure functions with no Django imports, so every rule below can be tested
without a database or a running server. The view layer turns these results
into JSON and looks up the guidance wording.

The rule that matters most is the last one: when the words are ambiguous we
would rather admit it than send someone confidently down the wrong route.
"""

from dataclasses import dataclass

from triage.classifier import DEFAULT_CLASSIFIER, Classifier
from triage.content import (
    ADVISER_GUIDANCE_KEY,
    NOT_SURE_OPTION_ID,
    ROUTES_BY_ID,
    Answer,
    Question,
    Route,
)

# The escape hatch added to a question when we guessed the route from someone's
# own words rather than being told it. Chosen deliberately as an answer in the
# same radio group, so correcting us costs the same effort as agreeing with us.
REJECT_ROUTE_ANSWER = Answer(
    id="not_my_problem",
    label="This is not what my problem is about",
    guidance_key=ADVISER_GUIDANCE_KEY,
)


@dataclass(frozen=True)
class RouteMatch:
    """A route we are proposing, and whether the person chose it themselves."""

    route: Route
    # True when the person picked the scenario, False when we inferred it from
    # their description. Inferred routes get the escape answer added.
    chosen_by_person: bool


def match_route(
    scenario: str | None,
    description: str | None,
    classifier: Classifier = DEFAULT_CLASSIFIER,
) -> RouteMatch | None:
    """Work out which route to offer, from a chosen scenario or a description.

    A chosen scenario always wins: if someone has told us what their problem is
    about, we do not second-guess them with a classifier. Choosing "I am not
    sure" is an answer in itself and goes to the fallback.

    The classifier is an argument so a test can supply its own, and so a
    model-backed one could be swapped in without touching anything else.
    """
    if scenario == NOT_SURE_OPTION_ID:
        return None

    if scenario is not None:
        route = ROUTES_BY_ID.get(scenario)
        return RouteMatch(route=route, chosen_by_person=True) if route else None

    if description is None:
        return None

    route_id = classifier.classify(description)
    inferred = ROUTES_BY_ID.get(route_id) if route_id else None
    return RouteMatch(route=inferred, chosen_by_person=False) if inferred else None


def question_for(match: RouteMatch) -> Question:
    """The follow-up question to ask, with an escape hatch if we guessed.

    When the person chose the scenario themselves the question is unchanged.
    When we inferred it from their words, they get one extra answer that says
    we were wrong, which sends them to the fallback rather than deeper into a
    route that does not fit.
    """
    question = match.route.question
    if match.chosen_by_person:
        return question
    return Question(
        id=question.id,
        text=question.text,
        answers=question.answers + (REJECT_ROUTE_ANSWER,),
    )


def resolve_answer(match: RouteMatch, answer_id: str) -> Answer | None:
    """Find the chosen answer, or None if it is not one we offered."""
    return next(
        (answer for answer in question_for(match).answers if answer.id == answer_id),
        None,
    )
