"""Create the sample guidance pages.

Dummy content, written for this exercise. It is deliberately *not* LEASE's
published wording: each page links out to lease-advice.org so the authoritative
text stays theirs. Running this twice is safe; existing pages are left alone.
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page

from guidance.models import GuidancePage

# Real section URLs on lease-advice.org, supplied rather than guessed. Tracking
# parameters are stripped: there is no reason to carry someone's referrer into
# a public service.
#
# The lease extension pages still point at the home page, because no verified
# URL for that section was available and an unchecked deep link risks a 404 at
# the moment a person least needs one. lease_url is editor-managed, so LEASE can
# correct those in Wagtail without a code change.
LEASE_ADVICE_HOME = "https://www.lease-advice.org/"

SAMPLE_GUIDANCE = [
    {
        "guidance_key": "service-charges-understanding",
        "lease_url": "https://www.lease-advice.org/costs-and-charges/service-charges/about-service-charges/",
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
        "lease_url": "https://www.lease-advice.org/costs-and-charges/service-charges/challenging-service-charges/",
        "title": "Questioning a service charge you think is wrong",
        "summary": (
            "A possible next step is to put your concern in writing to whoever sent "
            "the bill, and keep a copy. If that does not settle it, there is a "
            "tribunal that can decide whether a service charge is reasonable."
        ),
    },
    {
        "guidance_key": "lease-extension-more-than-80-years",
        "lease_url": "https://www.lease-advice.org/lease-extension/flats/informal-route/",
        "title": "Extending a lease with more than 80 years left",
        "summary": (
            "With more time in hand there is usually room to look at both ways of "
            "extending. This covers the informal route, where terms are agreed "
            "directly; the formal route works differently and has its own page."
        ),
    },
    {
        "guidance_key": "lease-extension-80-years-or-fewer",
        "lease_url": "https://www.lease-advice.org/lease-extension/flats/formal-route/",
        "title": "Extending a lease with 80 years or fewer left",
        "summary": (
            "The formal route follows steps set out in law and gives you rights a "
            "private agreement does not. Timing matters more as a lease shortens, "
            "so a possible next step is to read how that process runs."
        ),
    },
    {
        "guidance_key": "lease-extension-checking-your-lease",
        "lease_url": "https://www.lease-advice.org/lease-extension/flats/getting-started/",
        "title": "Finding out how long is left on your lease",
        "summary": (
            "Your own copy of the lease gives a start date and a length, and the "
            "Land Registry holds a copy of most registered leases. A possible next "
            "step is to start there, before working out which route suits you."
        ),
    },
    {
        "guidance_key": "repairs-inside-your-flat",
        "lease_url": "https://www.lease-advice.org/building-management/repairs/repairs-and-maintenance-in-leasehold-properties/",
        "title": "Repairs inside your own flat",
        "summary": (
            "Your lease normally divides responsibility between you and your "
            "landlord, and the split is not always obvious. A possible next step "
            "is to check what your lease says about the part that needs fixing."
        ),
    },
    {
        "guidance_key": "repairs-shared-areas",
        "lease_url": "https://www.lease-advice.org/building-management/repairs/repairs-and-maintenance-in-leasehold-properties/",
        "title": "Repairs to shared parts of a building",
        "summary": (
            "Shared parts such as roofs, hallways and lifts are usually the "
            "landlord's responsibility. A possible next step is to report the "
            "problem in writing and keep a record of when you reported it."
        ),
    },
    {
        "guidance_key": "service-charges-if-you-do-not-pay",
        "lease_url": "https://www.lease-advice.org/costs-and-charges/service-charges/if-you-do-not-pay/",
        "title": "If you cannot pay a service charge",
        "summary": (
            "Not paying has consequences, so a possible next step is to find out "
            "what they are before deciding what to do. Telling whoever sent the "
            "bill that there is a problem, in writing, is usually better than "
            "saying nothing."
        ),
    },
    {
        "guidance_key": "repairs-water-leaks",
        "lease_url": "https://www.lease-advice.org/building-management/repairs/water-leaks/",
        "title": "Water leaking into your home",
        "summary": (
            "Who deals with a leak depends on where it comes from, which is not "
            "always obvious from inside the flat. A possible next step is to report "
            "it in writing straight away and photograph the damage while it is "
            "fresh."
        ),
    },
    {
        "guidance_key": "repairs-not-being-fixed",
        "lease_url": "https://www.lease-advice.org/building-management/repairs/pre-action-protocol/",
        "title": "When a repair has been reported but not done",
        "summary": (
            "There is a recognised set of steps to follow before a disrepair case "
            "can go to court, and it starts with a written record of what you "
            "reported and when. A possible next step is to gather those dates "
            "together."
        ),
    },
    {
        "guidance_key": "management-problems",
        "lease_url": "https://www.lease-advice.org/building-management/management/leasehold-management-problems/",
        "title": "Problems with how a building is managed",
        "summary": (
            "Leaseholders have more say over management than is often realised. A "
            "possible next step is to find out which of those rights fits your "
            "situation before raising it."
        ),
    },
    {
        "guidance_key": "management-appoint-a-manager",
        "lease_url": "https://www.lease-advice.org/building-management/management/appointment-of-a-manager/",
        "title": "Having a different manager appointed",
        "summary": (
            "A tribunal can appoint a new manager where management has gone "
            "seriously wrong. A possible next step is to read what has to be shown "
            "before an application like that can succeed."
        ),
    },
    {
        "guidance_key": "disputes-tribunal",
        "lease_url": "https://www.lease-advice.org/disputes/tribunal/",
        "title": "Taking a matter to a tribunal",
        "summary": (
            "The tribunal handles many leasehold disputes and is designed to be "
            "used without a solicitor. A possible next step is to read how it works "
            "and what it can and cannot decide."
        ),
    },
    {
        "guidance_key": "right-to-manage-about",
        "lease_url": "https://www.lease-advice.org/building-management/right-to-manage/about-the-right-to-manage/",
        "title": "What the Right to Manage is",
        "summary": (
            "The Right to Manage lets leaseholders take over management of their "
            "building without having to prove anyone did anything wrong. A possible "
            "next step is to check whether your building qualifies."
        ),
    },
    {
        "guidance_key": "right-to-manage-setting-up",
        "lease_url": "https://www.lease-advice.org/building-management/right-to-manage/setting-up-the-right-to-manage/",
        "title": "Setting up a Right to Manage company",
        "summary": (
            "The process has strict steps and notices, and getting one wrong can "
            "mean starting again. A possible next step is to read the sequence "
            "through before serving anything."
        ),
    },
    {
        "guidance_key": "right-to-manage-running",
        "lease_url": "https://www.lease-advice.org/building-management/right-to-manage/running-a-right-to-manage-company/",
        "title": "Running a Right to Manage company",
        "summary": (
            "Once management transfers, the company takes on real duties and its "
            "directors take on responsibilities. A possible next step is to check "
            "what those are for your own role."
        ),
    },
    {
        "guidance_key": "fire-safety-risk-assessments",
        "lease_url": "https://www.lease-advice.org/building-management/fire-safety/fire-risk-assessments/",
        "title": "Fire risk assessments",
        "summary": (
            "Buildings with shared areas normally need a fire risk assessment, and "
            "leaseholders can usually ask about it. A possible next step is to find "
            "out who is responsible for having one done."
        ),
    },
    {
        "guidance_key": "fire-safety-measures",
        "lease_url": "https://www.lease-advice.org/building-management/fire-safety/fire-safety-measures/",
        "title": "Fire safety measures in a building",
        "summary": (
            "Alarms, fire doors and escape routes are part of how a building is "
            "kept safe. A possible next step is to read what is normally expected, "
            "so you can say clearly what seems to be missing."
        ),
    },
    {
        "guidance_key": "fire-safety-directors",
        "lease_url": "https://www.lease-advice.org/building-management/fire-safety/fire-safety-for-directors/",
        "title": "Fire safety duties for directors",
        "summary": (
            "Directors of a company that runs a building carry duties of their own "
            "for fire safety. A possible next step is to check what is expected of "
            "you in that role."
        ),
    },
    {
        "guidance_key": "service-charges-overview",
        "lease_url": "https://www.lease-advice.org/costs-and-charges/service-charges/",
        "title": "Service charges: where to start",
        "summary": (
            "If you are not sure yet what you need, the overview of service "
            "charges is a reasonable place to begin. Speaking to an adviser is "
            "also a sensible next step, and costs nothing."
        ),
    },
    {
        "guidance_key": "repairs-overview",
        "lease_url": "https://www.lease-advice.org/building-management/repairs/",
        "title": "Repairs: where to start",
        "summary": (
            "If you are not sure which part of the problem to tackle first, the "
            "repairs overview covers how responsibility is usually divided. "
            "Speaking to an adviser is also a sensible next step."
        ),
    },
    {
        "guidance_key": "management-overview",
        "lease_url": "https://www.lease-advice.org/building-management/management/",
        "title": "Building management: where to start",
        "summary": (
            "If you are not sure what kind of management problem you have, the "
            "overview sets out what leaseholders can usually expect. Speaking to "
            "an adviser is also a sensible next step."
        ),
    },
    {
        "guidance_key": "right-to-manage-overview",
        "lease_url": "https://www.lease-advice.org/building-management/right-to-manage/",
        "title": "Right to Manage: where to start",
        "summary": (
            "If you are not sure where you are up to, the Right to Manage overview "
            "explains the whole process from the beginning. Speaking to an adviser "
            "is also a sensible next step."
        ),
    },
    {
        "guidance_key": "fire-safety-overview",
        "lease_url": "https://www.lease-advice.org/building-management/fire-safety/",
        "title": "Fire safety: where to start",
        "summary": (
            "If you are not sure which part of fire safety your concern falls "
            "under, the overview covers the main duties and who holds them. "
            "Speaking to an adviser is also a sensible next step."
        ),
    },
    {
        "guidance_key": "fire-safety-who-pays",
        "lease_url": "https://www.lease-advice.org/building-management/fire-safety/leaseholder-protections/",
        "title": "Who pays for fire safety work",
        "summary": (
            "There are protections that limit what leaseholders can be charged for "
            "some fire safety problems, and they depend on the building and when "
            "the work is needed. A possible next step is to check which apply to "
            "you before agreeing to pay anything."
        ),
    },
    {
        "guidance_key": "fire-safety-selling",
        "lease_url": "https://www.lease-advice.org/building-management/fire-safety/selling-or-remortgaging-a-flat-with-fire-safety-issues/",
        "title": "Selling or remortgaging with fire safety issues",
        "summary": (
            "Fire safety problems can affect a sale or a mortgage, and buyers and "
            "lenders often ask for specific paperwork. A possible next step is to "
            "find out which documents your building should be able to provide."
        ),
    },
    {
        "guidance_key": "management-how-it-works",
        "lease_url": "https://www.lease-advice.org/building-management/management/how-leasehold-properties-are-managed/",
        "title": "How leasehold buildings are managed",
        "summary": (
            "Knowing who is supposed to do what, and where that comes from in your "
            "lease, makes it much easier to say when something has gone wrong. A "
            "possible next step is to read how the arrangement normally works."
        ),
    },
    {
        "guidance_key": "lease-extension-reforms",
        "lease_url": "https://www.lease-advice.org/lease-extension/leasehold-reforms/",
        "title": "Changes to the lease extension rules",
        "summary": (
            "The law in this area has been changing, and some changes affect what "
            "an extension costs and who can ask for one. A possible next step is to "
            "check what has actually come into force before deciding when to act."
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
                lease_url=entry.get("lease_url", LEASE_ADVICE_HOME),
            )
            parent.add_child(instance=page)
            page.save_revision().publish()
            created += 1
            self.stdout.write(f"Created: {entry['guidance_key']}")

        self.stdout.write(self.style.SUCCESS(f"Done. {created} page(s) created."))
