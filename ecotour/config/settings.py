"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.2.13.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

import environ
from drf_yasg import openapi

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# read env config
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
env_path = BASE_DIR.parent / ".env"
environ.Env.read_env(env_file=env_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")


# Define an environment variable to distinguish between development and production
ENVIRONMENT = env("DJANGO_ENVIRONMENT")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENVIRONMENT == "development"
DEBUG = True


ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True


# Application definition

INSTALLED_APPS = [
    "accounts",
    "tourlike",
    "tourspot",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_yasg",
    "rest_framework",
    "rest_framework_simplejwt",
    "community",
    "mainpage",
    "corsheaders",
    "mypage",
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if ENVIRONMENT == "development":

    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",  # 고정
            "NAME": env("DATABASE_NAME"),  # DB 이름
            "USER": env("DATABASE_USER"),  # 계정
            "PASSWORD": env("DATABASE_PW"),  # 암호
            "HOST": env("DATABASE_HOST"),  # IP
            "PORT": "3306",  # default
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"  # URL 경로는 슬래시로 시작하고 끝나야 합니다.
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # collectstatic으로 모아놓을 디렉토리
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]  # 프로젝트 수준의 static 디렉토리

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


if ENVIRONMENT == "development":
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
    MEDIA_URL = "/media/"

else:
    # S3 Settings for Media Files
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")

    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    AWS_MEDIA_LOCATION = "media"

    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/{AWS_MEDIA_LOCATION}/"


REST_FRAMEWORK = {"DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",)}

SIMPLE_JWT = {
    "USER_ID_FIELD": "user_id",
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}


AUTH_USER_MODEL = "accounts.CustomUser"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    "https://127.0.0.1:3000",
    # Add more origins as needed
]


CORS_ALLOW_HEADERS = ["accept", "accept-encoding", "authorization", "content-type", "dnt", "origin", "user-agent", "x-csrftoken", "x-requested-with"]

CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]


scope = ""
scope_param = f"&scope={scope}" if scope else ""
client_id = env("KAKAO_CLIENT_ID")
redirect_uri = env("SWAGGER_KAKAO_REDIRECT_URI")
link = f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code{scope_param}"


SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "SECURITY_DEFINITIONS": {
        "Kakao OAuth2": {
            "type": "oauth2",
            "flow": "authorizationCode",
            "authorizationUrl": link,
            "tokenUrl": "https://kauth.kakao.com/oauth/token",
            "in": "header",
        },
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",  # Specify that the token should be passed in the Authorization header
        },
        "X-CSRFToken": {
            "type": "apiKey",
            "name": "X-CSRFToken",
            "in": "header",  # Specify that the token should be passed in the Authorization header
        },
    },
    "DEFAULT_INFO": openapi.Info(
        title="Kakao OAuth API",
        default_version="v1",
        description="API for Kakao OAuth2 integration",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
    ),
}
