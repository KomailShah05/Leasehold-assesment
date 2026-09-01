import os

from .base import *  # noqa: F403

DEBUG = False

# No fallback on purpose: a missing key should stop the deploy, not quietly
# start the site with a guessable secret.
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

ALLOWED_HOSTS = [
    host.strip() for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if host.strip()
]

# The prototype is not deployed, but leaving production settings unhardened
# would mean the first real deployment started insecure by default.
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# A year, and only sensible once the site is genuinely HTTPS-only: browsers
# remember it, so it is hard to undo.
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Nothing here should ever be framed by another site.
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

# Do not leak the page someone came from when they follow a link out to LEASE.
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

try:
    from .local import *  # noqa: F403
except ImportError:
    pass
