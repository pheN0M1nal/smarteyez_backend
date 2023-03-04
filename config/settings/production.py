import heroku as heroku

from .base import *
import django_on_heroku

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
if env.bool("DJANGO_USE_MEMORY_DATABASE_AS_MAIN_DB", True):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": env.str("DJANGO_MAIN_DB_ENGINE"),
            "NAME": env.str("DJANGO_MAIN_DB_NAME"),
            "USER": env.str("DJANGO_MAIN_DB_USER"),
            "PASSWORD": env.str("DJANGO_MAIN_DB_PASSWORD"),
            "HOST": env.str("DJANGO_MAIN_DB_HOST"),
            "PORT": env.int("DJANGO_MAIN_DB_PORT", 5432),
        }
    }

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"
USING_MANAGED_STORAGE = False
DEVELOPMENT_MODE = False
django_on_heroku.settings(locals())