
from .base import *
import dj_database_url

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
    DATABASES={
        "default":dj_database_url.parse(os.environ.get('DJANGO_DATABASE_URL'))
    }



STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"