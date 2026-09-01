"""The triage rules.

Deterministic, and deliberately so. A person in difficulty needs an answer we
can explain, reproduce and test; a model that is usually right is worse here
than a rule that is always the same. There is no external API call in this
path, so the journey cannot fail because a third party is down.

Pure functions with no Django imports, so every rule below can be tested
without a database or a running server. The view layer turns these results
into JSON and looks up the guidance wording.

The rule that matters most is the last one: when the words are ambiguous we
would rather admit it than send someone confidently down the wrong route.
"""

from dataclasses import dataclass

from triage.content import (
    ADVISER_GUIDANCE_KEY,
    NOT_SURE_OPTION_ID,
    ROUTES,
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

# Free text has to clear this before we will name a route at all. One bare
# keyword ("bill") is a coincidence; we want a little more than that.
MINIMUM_SCORE = 2

# How far ahead the best route must be before we treat it as the answer. A tie,
# or a near tie, means the words genuinely fit two topics, and picking one would
# be a guess wearing a confident face.
MINIMUM_LEAD = 2


@dataclass(frozen=True)
class RouteMatch:
    """A route we are proposing, and whether the person chose it themselves."""

    route: Route
    # True when the person picked the scenario, False when we inferred it from
    # their description. Inferred routes get the escape answer added.
    chosen_by_person: bool


def normalise(text: str) -> str:
    """Lower-case and collapse whitespace, so matching is not tripped by typing."""
    return " ".join(text.lower().split())


def score_route(text: str, route: Route) -> int:
    """How strongly a description points at one route.

    Longer keyword phrases count for more than single words, because "lease
    extension" is real evidence and "lease" on its own is not: almost every
    person using this service will write the word "lease" at some point.
    """
    normalised = normalise(text)
    return sum(len(keyword.split()) for keyword in route.keywords if keyword in normalised)


def classify(text: str) -> Route | None:
    """Pick the route a description points at, or None if we cannot tell.

    Returns None in three separate situations, all of which lead to the
    fallback: nothing matched, the best match was too weak to trust, or two
    routes were close enough that choosing between them would be a guess.
    """
    if not text.strip():
        return None

    scores = sorted(
        ((route, score_route(text, route)) for route in ROUTES),
        key=lambda pair: pair[1],
        reverse=True,
    )

    best_route, best_score = scores[0]
    runner_up_score = scores[1][1] if len(scores) > 1 else 0

    if best_score < MINIMUM_SCORE:
        return None
    if best_score - runner_up_score < MINIMUM_LEAD:
        return None
    return best_route


def match_route(scenario: str | None, description: str | None) -> RouteMatch | None:
    """Work out which route to offer, from a chosen scenario or a description.

    A chosen scenario always wins: if someone has told us what their problem is
    about, we do not second-guess them with keyword matching. Choosing "I am not
    sure" is an answer in itself and goes to the fallback.
    """
    if scenario == NOT_SURE_OPTION_ID:
        return None

    if scenario is not None:
        route = ROUTES_BY_ID.get(scenario)
        return RouteMatch(route=route, chosen_by_person=True) if route else None

    if description is None:
        return None

    inferred = classify(description)
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
