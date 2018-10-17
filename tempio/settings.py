import dj_database_url

import base64
import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.getenv('DATA_DIR', BASE_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    secret_path = os.path.join(DATA_DIR, 'secret.key')
    if os.path.exists(secret_path):
        SECRET_KEY = open(secret_path, 'r').read().strip()
    else:
        with open(os.path.join(DATA_DIR, 'secret.key'), 'w') as f:
            SECRET_KEY = base64.b64encode(os.urandom(32)).decode('ascii')
            f.write(SECRET_KEY)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'true') == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tempio',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'tempio.middleware.AnonymousUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tempio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tempio.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases


DATABASES = {
    'default': dj_database_url.config(default='sqlite:///{}'.format(os.path.join(DATA_DIR, 'db.sqlite3'))),
}


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.getenv('TIME_ZONE', 'US/Eastern')
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.getenv('STATIC_ROOT', os.path.join(BASE_DIR, 'static'))

TEMPIO_COOKIE_NAME = os.getenv('TEMPIO_COOKIE_NAME', 'tempio_user')
TEMPIO_COOKIE_EXPIRATION = int(os.getenv('TEMPIO_COOKIE_EXPIRATION', 9000))  # days
TEMPIO_MAX_SIZE = int(os.getenv('TEMPIO_MAX_SIZE', 1024 * 1024 * 5))  # 5 MB
