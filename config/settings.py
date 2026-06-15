"""
Настройки Django для проекта «Служба заявок» (Help Desk).
ПМ.11 — Разработка, администрирование и защита баз данных.
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Загрузка переменных окружения из .env (если файл есть)
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes", "on")


# --- Безопасность ---
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-dev-key-change-me-in-production-0123456789",
)
DEBUG = env_bool("DEBUG", True)

# Хосты: локально разрешаем всё, на проде берём из переменной окружения
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Render и другие хостинги пробрасывают внешний домен через эту переменную
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = [
    o for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o
]
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")


# --- Приложения ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "helpdesk",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --- База данных ---
# Локально по умолчанию SQLite; на проде задаётся DATABASE_URL (PostgreSQL).
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}


# --- Кастомная модель пользователя (с ролями) ---
AUTH_USER_MODEL = "helpdesk.User"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "ticket_list"
LOGOUT_REDIRECT_URL = "login"


# --- Валидация паролей (защита учётных данных) ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --- Локализация ---
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True


# --- Статика (WhiteNoise для деплоя) ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Доп. безопасность для продакшена ---
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
