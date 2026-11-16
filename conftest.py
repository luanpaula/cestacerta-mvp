import django
from django.conf import settings

def pytest_configure():
    if not settings.configured:
        settings.configure(
            SECRET_KEY="test-secret-key-cestacerta",
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "cestacerta",
            ],
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
        )
        django.setup()
