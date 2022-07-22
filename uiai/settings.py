import configparser
import os
from datetime import timedelta
from pathlib import Path
from corsheaders.defaults import default_methods
from corsheaders.defaults import default_headers

# Read From settings.ini
config = configparser.RawConfigParser()
config.read('settings.ini')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config['GENERAL'].get('SECRET_KEY', 'test')

DEBUG = config['GENERAL'].getboolean('DEBUG', True)

ALLOWED_HOSTS = config['GENERAL'].get('ALLOWED_HOSTS').split(",")


HASH_SALT = config['GENERAL'].get('SALT')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'core',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'authenticate',
    'account',
    'media',
    'blog',
    'send_email',
    'general'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'uiai.urls'

WSGI_APPLICATION = 'uiai.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': config['DATABASE'].get('ENGINE', 'django.db.backends.sqlite3'),
#         'HOST': config['DATABASE'].get('HOST', ''),
#         'PORT': config['DATABASE'].get('PORT', ''),
#         'NAME': config['DATABASE'].get('NAME', ''),
#         'USER': config['DATABASE'].get('USER', ''),
#         'PASSWORD': config['DATABASE'].get('PASSWORD', ''),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# Logger
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': config['LOGGING'].get('LEVEL', 'INFO')
    },
}

# Simple Jwt
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(config['SIMPLE_JWT'].get('access_token_lifetime_minutes'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=int(config['SIMPLE_JWT'].get('refresh_token_lifetime_minutes'))),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'hash',
    'USER_ID_CLAIM': 'hash',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),

    # COOKIE and SESSIONS
    # Cookie name. Enables cookies if value is set.
    'AUTH_COOKIE': 'access_token',
    'AUTH_COOKIE_REFRESH': 'refresh_token',
    # A string like "example.com", or None for standard domain cookie.
    'AUTH_COOKIE_DOMAIN': None,
    # Whether the auth cookies should be secure (https:// only).
    'AUTH_COOKIE_SECURE': True,
    # Http only cookie flag.It's not fetch by javascript.
    'AUTH_COOKIE_HTTP_ONLY': False,
    'AUTH_COOKIE_PATH': '/',  # The path of the auth cookie.
    'AUTH_COOKIE_SAMESITE': 'None',  # Whether to set the
}
# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# CORS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    "Accept",
    "Content-type",
    "Access-Control-Allow-Origin",
    "Access-Control-Allow-Methods",
    "Access-Control-Allow-Headers",
    "Set-Cookie",
    "Authorization"
]
CORS_ALLOW_METHODS = list(default_methods)
CORS_ALLOW_CREDENTIALS = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = 'staticfiles'

# Media
# MEDIA_URL = 'storage/'
# MEDIA_ROOT = BASE_DIR / 'storage'
MEDIA_ROOT = os.path.join(BASE_DIR, 'storage').replace('\\', '/')
MEDIA_URL = '/storage/'

# Auth user model
AUTH_USER_MODEL = 'account.User'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PATH_SEPARATOR = '/'

# Media CD prefix
CDN_SERVER_PREFIX = config['MEDIA'].get(
    'CDN_SERVER_PREFIX', 'http://127.0.0.1:8000')

# SESSIONS
SESSION_COOKIE_SAMESITE = 'None'
CRSF_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = False

# Front url
LOGIN_URL = 'https://ui-ai.ir/login'
REGISTER_URL = 'https://ui-ai.ir/singup'
EMAIL_VERIFY_URL = 'https://api.ui-ai.ir/verify-email/'
RESET_PASSWORD_URL = 'https://ui-ai.ir/reset-password/'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config['EMAIL'].get('email_host')
EMAIL_USE_TLS = config['EMAIL'].get('email_use_tls')
EMAIL_PORT = config['EMAIL'].get('email_port')
EMAIL_HOST_USER = config['EMAIL'].get('email_host_user')
EMAIL_HOST_PASSWORD = config['EMAIL'].get('email_host_password')
EMAIL_VERIFY_SALT = config['EMAIL'].get('email_verify_salt')

# Reser password
RESET_PASSWORD_TOKEN_LIFE_TIME = timedelta(minutes=int(config['RESET_PASSWORD'].get('reset_password_token_lifetime_minutes')))
RESET_PASSWORD_SALT = config['RESET_PASSWORD'].get('reset_password_salt')

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 86400  # sec
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_NAME = 'sessionid'
# SESSION_COOKIE_SECURE = False


CSRF_TRUSTED_ORIGINS = ['https://*.ui-ai.ir', 'https://*.127.0.0.1', 'https://ui-ai.ir',]

DEFAULT_AVATAR_URL = '/storage/user/avatar/default.jpg'
DEFAULT_BANNER_URL = '/storage/user/banner/default.jpg'

