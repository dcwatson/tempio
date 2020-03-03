import base64
import os

import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.getenv("DATA_DIR", BASE_DIR)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    secret_path = os.path.join(DATA_DIR, "secret.key")
    if os.path.exists(secret_path):
        SECRET_KEY = open(secret_path, "r").read().strip()
    else:
        with open(os.path.join(DATA_DIR, "secret.key"), "w") as f:
            SECRET_KEY = base64.b64encode(os.urandom(32)).decode("ascii")
            f.write(SECRET_KEY)


DEBUG = os.getenv("DEBUG", "true") == "true"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tempio",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "tempio.middleware.AnonymousUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tempio.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "tempio.utils.context_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "tempio.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(default="sqlite:///{}".format(os.path.join(DATA_DIR, "db.sqlite3"))),
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "US/Eastern")
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.getenv("STATIC_ROOT", os.path.join(BASE_DIR, "static"))

TEMPIO_SITE_NAME = os.getenv("TEMPIO_SITE_NAME", "temp")
TEMPIO_COOKIE_NAME = os.getenv("TEMPIO_COOKIE_NAME", "tempio_user")
TEMPIO_COOKIE_EXPIRATION = int(os.getenv("TEMPIO_COOKIE_EXPIRATION", 365))  # in days
TEMPIO_MAX_SIZE = int(os.getenv("TEMPIO_MAX_SIZE", 1024 * 1024 * 5))  # 5 MB
TEMPIO_DEFAULT_EXPIRATION = int(os.getenv("TEMPIO_DEFAULT_EXPIRATION", 1))  # in days
