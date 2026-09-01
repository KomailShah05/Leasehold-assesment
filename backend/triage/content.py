"""The routes a person can be sent down, and the words used to offer them.

This module holds *routing* only: which scenarios exist, what we ask about
each one, and which piece of guidance each answer points at. The guidance
prose itself lives in Wagtail so that LEASE editors own it, keyed by
``guidance_key``.

Everything here is plain data. It is deliberately small and deliberately
boring, so that a reviewer can read the whole taxonomy in one sitting and a
test can assert against it without booting Django.
"""

from dataclasses import dataclass

# Shown when we are not confident enough to pick a route. Also used as the
# destination for any "I'm not sure" answer, because guessing at someone's
# situation is worse than handing them to a person.
ADVISER_GUIDANCE_KEY = "talk-to-an-adviser"


@dataclass(frozen=True)
class Answer:
    """One option in the follow-up question, and where choosing it leads."""

    id: str
    label: str
    guidance_key: str


@dataclass(frozen=True)
class Question:
    """The single follow-up question we ask once a route is known."""

    id: str
    text: str
    answers: tuple[Answer, ...]


@dataclass(frozen=True)
class Route:
    """A scenario a person can choose, or that their words can match.

    ``label`` is the plain-English wording a person reads first. ``legal_term``
    is the phrase LEASE and the legislation actually use; it sits inside the
    same label in smaller text so screen reader users hear it too, rather than
    being hidden from them behind a tooltip.

    ``keywords`` are matched against free text. They are ordinary words people
    use about their home, not legal vocabulary, because someone who knew the
    legal vocabulary would probably not need this tool.
    """

    id: str
    label: str
    legal_term: str
    keywords: tuple[str, ...]
    question: Question


SERVICE_CHARGES = Route(
    id="service_charges",
    label="I have a question about a bill or charge",
    legal_term="Service charges and administration charges",
    keywords=(
        "service charge",
        "bill",
        "charge",
        "invoice",
        "demand",
        "sinking fund",
        "reserve fund",
        "ground rent",
        "management fee",
        "budget",
        "accounts",
        "overcharged",
    ),
    question=Question(
        id="service_charges_focus",
        text="What would you most like help with?",
        answers=(
            Answer(
                id="understand",
                label="Understanding what I am being charged for",
                guidance_key="service-charges-understanding",
            ),
            Answer(
                id="challenge",
                label="Questioning a charge I think is wrong",
                guidance_key="service-charges-challenging",
            ),
            Answer(
                id="unsure",
                label="I am not sure yet",
                guidance_key=ADVISER_GUIDANCE_KEY,
            ),
        ),
    ),
)

LEASE_EXTENSIONS = Route(
    id="lease_extensions",
    label="I want to know about extending my lease",
    legal_term="Lease extension and buying the freehold",
    keywords=(
        "lease extension",
        "extend my lease",
        "extending",
        "years left",
        "short lease",
        "running out",
        "freehold",
        "freeholder",
        "premium",
        "renew my lease",
    ),
    question=Question(
        id="lease_extensions_term",
        text="Roughly how many years are left on your lease?",
        answers=(
            Answer(
                id="more_than_80",
                label="More than 80 years",
                guidance_key="lease-extension-more-than-80-years",
            ),
            Answer(
                id="80_or_fewer",
                label="80 years or fewer",
                guidance_key="lease-extension-80-years-or-fewer",
            ),
            Answer(
                id="unknown",
                label="I do not know",
                guidance_key="lease-extension-checking-your-lease",
            ),
        ),
    ),
)

REPAIRS = Route(
    id="repairs",
    label="Something needs repairing and it is not being fixed",
    legal_term="Repairs, maintenance and disrepair",
    keywords=(
        "repair",
        "repairs",
        "broken",
        "damp",
        "mould",
        "leak",
        "leaking",
        "roof",
        "window",
        "heating",
        "lift",
        "boiler",
        "not been fixed",
        "maintenance",
    ),
    question=Question(
        id="repairs_location",
        text="Where is the problem?",
        answers=(
            Answer(
                id="inside_flat",
                label="Inside my own flat",
                guidance_key="repairs-inside-your-flat",
            ),
            Answer(
                id="shared_area",
                label="In a shared part of the building, such as a roof, hallway or lift",
                guidance_key="repairs-shared-areas",
            ),
            Answer(
                id="unsure",
                label="I am not sure",
                guidance_key=ADVISER_GUIDANCE_KEY,
            ),
        ),
    ),
)

# Order matters: this is the order the radio buttons appear in.
ROUTES: tuple[Route, ...] = (SERVICE_CHARGES, LEASE_EXTENSIONS, REPAIRS)

ROUTES_BY_ID: dict[str, Route] = {route.id: route for route in ROUTES}

# The fourth radio button, in the same group as the three routes above rather
# than tucked away as a separate link.
NOT_SURE_OPTION_ID = "not_sure"
NOT_SURE_OPTION_LABEL = "I am not sure which of these fits"

# What we say when we cannot place someone. It admits the limit rather than
# guessing, and always offers a person.
FALLBACK_TITLE = "We could not match this to one of our topics"
FALLBACK_MESSAGE = (
    "This prototype only covers a few common topics, so it may simply not "
    "recognise your situation. That does not mean nothing can be done about it."
)
FALLBACK_GUIDANCE_KEY = ADVISER_GUIDANCE_KEY
