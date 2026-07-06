from pathlib import Path
from datetime import timedelta

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY", default="super-secret-key")

DEBUG = config("DEBUG", default="False", cast=str) == "True"

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*").split(",")


# Application definition

DEFAULT_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "drf_spectacular",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
]

MAIN_APPS = [
    "apps.user",
    "apps.chat",
    "apps.category",
    "apps.notification",
    "apps.authentication",
]

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + MAIN_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# Database

DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", cast=str, default="django.db.backends.sqlite3"),
        "NAME": config("DB_NAME", cast=str, default=BASE_DIR / "db.sqlite3"),
        "USER": config("DB_USER", cast=str, default="db_user"),
        "PASSWORD": config("DB_PASSWORD", cast=str, default="db_password"),
        "HOST": config("DB_HOST", cast=str, default="localhost"),
        "PORT": config("DB_PORT", cast=int, default=5432),
    }
}

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "apps.common.validators.UpperLowerCasePasswordValidator",
    },
]


# Internationalization

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Default User Model
AUTH_USER_MODEL = "user.User"

# REST Framework

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # 📄 Pagination
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

# Simple JWT
SIMPLE_JWT = {
    "SIGNING_KEY": config(
        "SIGNING_KEY",
        cast=str,
        default="4d7d8b1f0d4c7e7a0dfe2fd2b6a59c95fbd4c07d31d54af53c4cb24fd87dce12",
    ),
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=config("ACCESS_TOKEN_LIFETIME_MIN", cast=int, default=15)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=config("REFRESH_TOKEN_LIFETIME_DAY", cast=int, default=1)
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

# Otp expire seconds

OTP_EXPIRY_SECONDS = config("OTP_EXPIRY_SECONDS", cast=int, default=300)

# DRF Spectecular

SPECTACULAR_SETTINGS = {
    "TITLE": "Rest API",
    "DESCRIPTION": "Rest API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SERVE_PERMISSIONS": [],
    "SERVE_AUTHENTICATION": ["rest_framework.authentication.BasicAuthentication"],
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "filter": True,
        "persistAuthorization": True,
        "defaultModelsExpandDepth": -1,
    },
    "POSTPROCESSING_HOOKS": [],
}

# Email

EMAIL_BACKEND = config(
    "EMAIL_BACKEND", cast=str, default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("config", default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="defaultfromemail@example.com")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", "defaultfromemail@example.com")
ACCOUNT_ACTIVATION_TEMPLATE = config(
    "ACCOUNT_ACTIVATION_TEMPLATE", cast=str, default=""
)
PASSWORD_RESET_TEMPLATE = config("PASSWORD_RESET_TEMPLATE", cast=str, default="")

# Redis

REDIS_HOST = config("REDIS_HOST", cast=str, default="localhost")
REDIS_PORT = config("REDIS_PORT", cast=int, default=6379)

# Channel

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}

