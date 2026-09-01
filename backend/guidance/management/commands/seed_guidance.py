"""Create the sample guidance pages.

Dummy content, written for this exercise. It is deliberately *not* LEASE's
published wording: each page links out to lease-advice.org so the authoritative
text stays theirs. Running this twice is safe; existing pages are left alone.
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page

from guidance.models import GuidancePage

# Placeholder until an editor sets the specific page. Pointing every route at
# the advice guide index is honest about being a prototype; inventing deep
# links we have not verified would risk sending someone to a 404.
LEASE_ADVICE_GUIDE = "https://www.lease-advice.org/advice-guide/"

SAMPLE_GUIDANCE = [
    {
        "guidance_key": "service-charges-understanding",
        "title": "Understanding a service charge bill",
        "summary": (
            "A possible next step is to ask your landlord or managing agent for a "
            "written summary of what the charge covers. Leaseholders can normally "
            "ask to see the accounts behind a bill, and your lease sets out what "
            "you can be charged for."
        ),
    },
    {
        "guidance_key": "service-charges-challenging",
        "title": "Questioning a service charge you think is wrong",
        "summary": (
            "A possible next step is to put your concern in writing to whoever sent "
            "the bill, and keep a copy. If that does not settle it, there is a "
            "tribunal that can decide whether a service charge is reasonable."
        ),
    },
    {
        "guidance_key": "lease-extension-more-than-80-years",
        "title": "Extending a lease with more than 80 years left",
        "summary": (
            "With a longer lease there is usually less urgency, so a possible next "
            "step is to read up on how extensions work before approaching anyone. "
            "Costs tend to rise as a lease gets shorter, so it is worth knowing "
            "your timing."
        ),
    },
    {
        "guidance_key": "lease-extension-80-years-or-fewer",
        "title": "Extending a lease with 80 years or fewer left",
        "summary": (
            "Shorter leases usually cost more to extend, and the 80-year mark "
            "matters. A possible next step is to get advice early rather than "
            "waiting, so you understand the likely cost and the steps involved."
        ),
    },
    {
        "guidance_key": "lease-extension-checking-your-lease",
        "title": "Finding out how long is left on your lease",
        "summary": (
            "A possible next step is to check your own copy of the lease, which "
            "gives a start date and a length. If you cannot find it, the Land "
            "Registry holds a copy of most registered leases."
        ),
    },
    {
        "guidance_key": "repairs-inside-your-flat",
        "title": "Repairs inside your own flat",
        "summary": (
            "Your lease normally divides responsibility between you and your "
            "landlord, and the split is not always obvious. A possible next step "
            "is to check what your lease says about the part that needs fixing."
        ),
    },
    {
        "guidance_key": "repairs-shared-areas",
        "title": "Repairs to shared parts of a building",
        "summary": (
            "Shared parts such as roofs, hallways and lifts are usually the "
            "landlord's responsibility. A possible next step is to report the "
            "problem in writing and keep a record of when you reported it."
        ),
    },
    {
        "guidance_key": "talk-to-an-adviser",
        "title": "Talking to an adviser",
        "summary": (
            "This prototype only recognises a few common topics, and yours may "
            "simply not be one of them. LEASE gives free initial advice to "
            "leaseholders, and speaking to an adviser is a sensible next step."
        ),
    },
]


class Command(BaseCommand):
    help = "Create the sample guidance pages used by the triage routes."

    def handle(self, *args: object, **options: object) -> None:
        parent = Page.objects.filter(depth=2).first()
        if parent is None:
            self.stderr.write("No home page found. Run migrate first.")
            return

        created = 0
        for entry in SAMPLE_GUIDANCE:
            if GuidancePage.objects.filter(guidance_key=entry["guidance_key"]).exists():
                self.stdout.write(f"Already present: {entry['guidance_key']}")
                continue

            page = GuidancePage(
                title=entry["title"],
                slug=entry["guidance_key"],
                guidance_key=entry["guidance_key"],
                summary=entry["summary"],
                lease_url=LEASE_ADVICE_GUIDE,
            )
            parent.add_child(instance=page)
            page.save_revision().publish()
            created += 1
            self.stdout.write(f"Created: {entry['guidance_key']}")

        self.stdout.write(self.style.SUCCESS(f"Done. {created} page(s) created."))
