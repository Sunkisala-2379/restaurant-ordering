"""
ASGI config for restaurant_ordering project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_ordering.settings')

application = get_asgi_application()
