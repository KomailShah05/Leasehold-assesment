import os

from .base import *  # noqa: F403

DEBUG = True

# A throwaway key is fine for local development only; production reads a real
# one from the environment and refuses to start without it.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "django-insecure-local-development-key-not-for-deployment"
)

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

try:
    from .local import *  # noqa: F403
except ImportError:
    pass
