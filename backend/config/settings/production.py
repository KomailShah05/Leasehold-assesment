import os

from .base import *  # noqa: F403

DEBUG = False

# No fallback on purpose: a missing key should stop the deploy, not quietly
# start the site with a guessable secret.
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

ALLOWED_HOSTS = [
    host.strip() for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if host.strip()
]

try:
    from .local import *  # noqa: F403
except ImportError:
    pass
