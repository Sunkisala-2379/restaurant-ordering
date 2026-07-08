#!/usr/bin/env python
"""
Production-ready script to create a Django superuser if one does not exist.
Reads credentials from environment variables with sensible defaults for development.
"""

import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_ordering.settings')

    try:
        import django
        django.setup()
    except ImportError:
        print('Error: Django is not installed.')
        sys.exit(1)

    from django.contrib.auth import get_user_model

    User = get_user_model()

    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@smartrestaurant.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin12345')

    if User.objects.filter(username=username).exists():
        print(f'Superuser "{username}" already exists. Skipping creation.')
        return

    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
    )
    print(f'Superuser "{username}" created successfully.')


if __name__ == '__main__':
    main()
