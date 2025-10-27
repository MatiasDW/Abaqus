"""
ASGI config for config project.

Exposes the ASGI callable as a module-level variable named `application`.
Docs: https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Ensure Django settings are loaded
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# For now we use pure Django ASGI (no Channels / websockets)
application = get_asgi_application()
