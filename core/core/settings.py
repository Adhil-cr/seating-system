import os
import sys
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv


VALID_EXAMCELL_MODES = {"development", "cloud", "standalone"}
TRUE_VALUES = {"1", "true", "yes", "on"}


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in TRUE_VALUES


FROZEN = getattr(sys, "frozen", False)
_initial_mode = os.getenv("EXAMCELL_MODE", "").strip().lower()

if not FROZEN and _initial_mode != "standalone":
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
_mode = os.getenv("EXAMCELL_MODE", _initial_mode).strip().lower()

if FROZEN:
    EXAMCELL_MODE = "standalone"
elif _mode in VALID_EXAMCELL_MODES:
    EXAMCELL_MODE = _mode
elif DATABASE_URL:
    EXAMCELL_MODE = "cloud"
else:
    EXAMCELL_MODE = "development"

STANDALONE = EXAMCELL_MODE == "standalone"
CLOUD = EXAMCELL_MODE == "cloud"
USE_SQLITE = env_bool("USE_SQLITE", STANDALONE)
DEBUG = False if STANDALONE else env_bool("DEBUG", False)

SOURCE_CORE_DIR = Path(__file__).resolve().parent.parent
SOURCE_PROJECT_DIR = SOURCE_CORE_DIR.parent

if FROZEN:
    BUNDLE_DIR = Path(sys._MEIPASS).resolve()
    APP_DIR = Path(sys.executable).resolve().parent
else:
    BUNDLE_DIR = SOURCE_PROJECT_DIR
    APP_DIR = SOURCE_CORE_DIR

CORE_DIR = BUNDLE_DIR if FROZEN else SOURCE_CORE_DIR
PROJECT_DIR = BUNDLE_DIR if FROZEN else SOURCE_PROJECT_DIR
BASE_DIR = CORE_DIR
RUNTIME_DATA_ROOT = Path(
    os.getenv("RUNTIME_DATA_ROOT", str(APP_DIR / "runtime_data"))
)

# SECURITY
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-me")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    f"http://{host}"
    for host in ALLOWED_HOSTS
    if host not in ["127.0.0.1", "localhost"]
]

# TEMP for AWS (no HTTPS yet)
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# APPLICATIONS
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "storages",

    "accounts",
    "students",
    "exams",
    "halls",
    "seating",
    "dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if CLOUD and not USE_SQLITE:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "core.urls"

TEMPLATE_DIR = (
    BUNDLE_DIR / "templates"
    if STANDALONE
    else PROJECT_DIR / "templates"
)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
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

WSGI_APPLICATION = "core.wsgi.application"

# DATABASE CONFIGURATION
if USE_SQLITE:
    default_sqlite_path = APP_DIR / "examcell.sqlite3" if STANDALONE else BASE_DIR / "examcell.sqlite3"
    db_path = Path(os.getenv("SQLITE_DB_PATH", str(default_sqlite_path)))
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(db_path),
        }
    }
elif DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
            "CONN_MAX_AGE": 600,
        }
    }

# AUTH
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "/"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# INTERNATIONAL
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# STATIC FILES
STATIC_URL = "/static/"

STATIC_SOURCE_DIR = (
    BUNDLE_DIR / "static"
    if STANDALONE
    else PROJECT_DIR / "static"
)

STANDALONE_STATIC_DIR = STATIC_SOURCE_DIR

STATICFILES_DIRS = [
    STATIC_SOURCE_DIR
]
STATIC_ROOT = Path(
    os.getenv(
        "STATIC_ROOT",
        str((APP_DIR if STANDALONE else BASE_DIR) / "staticfiles"),
    )
)

if CLOUD and not USE_SQLITE:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
else:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# MEDIA FILES
MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv(
    "MEDIA_ROOT",
    str(APP_DIR / "media" if STANDALONE else PROJECT_DIR / "media"),
)
if STANDALONE:
    print("=" * 60)
    print("ExamCell Settings")
    print("MODE =", EXAMCELL_MODE)
    print("FROZEN =", FROZEN)
    print("BUNDLE_DIR =", BUNDLE_DIR)
    print("APP_DIR =", APP_DIR)
    print("STATIC_SOURCE_DIR =", STATIC_SOURCE_DIR)
    print("TEMPLATE_DIR =", TEMPLATE_DIR)
    print("MEDIA_ROOT =", MEDIA_ROOT)
    print("RUNTIME_DATA_ROOT =", RUNTIME_DATA_ROOT)
    print("=" * 60)

# BACKBLAZE (OPTIONAL)
if USE_SQLITE:
    B2_STORAGE_ENABLED = False
else:
    B2_STORAGE_ENABLED = env_bool("B2_STORAGE_ENABLED", False)

if B2_STORAGE_ENABLED:
    AWS_ACCESS_KEY_ID = os.getenv("B2_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("B2_APP_KEY", "")
    AWS_STORAGE_BUCKET_NAME = os.getenv("B2_BUCKET", "")
    AWS_S3_ENDPOINT_URL = os.getenv("B2_ENDPOINT", "")
    AWS_S3_REGION_NAME = os.getenv("B2_REGION", "")

    AWS_S3_ADDRESSING_STYLE = "path"
    AWS_QUERYSTRING_AUTH = False

    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# EMAIL
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", False)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")

if EMAIL_HOST:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
