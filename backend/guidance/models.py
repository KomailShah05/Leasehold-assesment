from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page


class GuidancePage(Page):
    """A single piece of signposting content, owned by LEASE editors.

    The triage rules never contain guidance wording. They only produce a
    ``guidance_key``, and this model is what that key resolves to, so the words
    a person finally reads have been through an editor rather than through a
    developer or a language model.
    """

    guidance_key = models.SlugField(
        max_length=100,
        unique=True,
        help_text=(
            "The identifier the triage rules use to find this page. "
            "Changing it will break the route that points here."
        ),
    )
    summary = models.TextField(
        max_length=600,
        help_text=(
            "A short plain-English description of the possible next step. "
            "Signpost only: describe what a person could do and who can help, "
            "and do not give legal advice."
        ),
    )
    lease_url = models.URLField(
        verbose_name="LEASE guidance URL",
        help_text=(
            "The page on lease-advice.org holding the authoritative guidance. "
            "The prototype links out to it rather than copying its wording."
        ),
    )

    # Plain text, not rich text: the summary is rendered by React as text, so
    # there is no path from editor content to markup in the browser.
    content_panels = Page.content_panels + [
        FieldPanel("guidance_key"),
        FieldPanel("summary"),
        FieldPanel("lease_url"),
    ]

    # These pages are read through the API, never browsed as a website.
    subpage_types: list[str] = []

    class Meta:
        verbose_name = "guidance page"

    def __str__(self) -> str:
        return self.title
