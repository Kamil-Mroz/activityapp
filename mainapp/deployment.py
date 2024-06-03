import os
from .settings import *
from .settings import BASE_DIR

ALLOWED_HOSTS = [os.environ["WEBSITE_HOSTNAME"]]
CSRF_TRUSTED_ORIGINS = ["https://" + os.environ["WEBSITE_HOSTNAME"]]

DEBUG = False


MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

connections_string = os.environ["AZURE_POSTGRESQL_CONNECTIONSTRING"]
parameters = {
    pair.split("="): pair.split("=")[1] for pair in connections_string.split(" ")
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": parameters["dbname"],
        "USER": parameters["user"],
        "PASSWORD": parameters["password"],
        "HOST": parameters["host"],
    }
}


RECAPTCHA_PUBLIC_KEY = os.environ["RECAPTCHA_PUBLIC_KEY"]
RECAPTCHA_PRIVATE_KEY = os.environ["RECAPTCHA_PRIVATE_KEY"]

# WKHTMLTOPDF_PATH = env("WKHTMLTOPDF_PATH")


SECRET_KEY = os.environ["SECRET"]
