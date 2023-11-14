"""
Django settings for antrobackend project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import datetime
import environ
import os

from dotenv import load_dotenv

load_dotenv()
env = environ.Env(
    DEBUG=(bool, False)
)

READ_DOT_ENV_FILE = env('READ_DOT_ENV_FILE')
if READ_DOT_ENV_FILE:
    environ.Env.read_env()
    TWO_FACTOR_API_KEY= env('TWO_FACTOR_API_KEY')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-2t*kv1$mt2k*7+bz2r$8=0l9d^28yhrnlf9gz1p1_k3#zrn&%x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=1),
}


# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'django_extensions',
#    'push_notifications',
    'rest_framework',
    'users',
    'phonenumber_field',
    'django.contrib.gis',
    'profiles',
    'chat',
    'organisation',
]

# AUTH_USER_MODEL = 'users.models.User'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'middlewares.requestData.RequestLogMiddleWare'
]

ROOT_URLCONF = 'antrobackend.urls'

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

WSGI_APPLICATION = 'antrobackend.wsgi.application'
ASGI_APPLICATION = "antrobackend.asgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Local
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'antroproject',
        'USER': 'antrouser',
        'PASSWORD': 'QazPlm@123',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

# Server
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.contrib.gis.db.backends.postgis',
#         'NAME': 'antro',
#         'USER': 'antrouser',
#         'PASSWORD': 'Pass_1234',
#         'HOST': 'localhost',
#         'PORT': 5432,
#     }
# }

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


AUTHENTICATION_BACKENDS = [
    'users.auth_backends.CustomUserBackend',
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_PROFILE_MODULE = 'users.User'

AUTH_USER_MODEL = 'users.User'


#GDAL_LIBRARY_PATH="/opt/homebrew/Cellar/gdal/3.6.3/lib/libgdal.dylib"
#GEOS_LIBRARY_PATH="/opt/homebrew/Cellar/geos/3.11.1/lib/libgeos_c.dylib"

# Local
# GDAL_LIBRARY_PATH="/opt/homebrew/Cellar/gdal/3.6.4_6/lib/libgdal.dylib"
# GEOS_LIBRARY_PATH="/opt/homebrew/Cellar/geos/3.11.2/lib/libgeos_c.dylib"

ALLOWED_HOSTS = ['*']

# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static/')
# ]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'staticfiles')

STATICFILES_DIR = {
    os.path.join(BASE_DIR , "/public/static")
}
MEDIA_ROOT =  os.path.join(BASE_DIR, 'public/static') 
MEDIA_URL = '/media/'


# Push notification settings
PUSH_NOTIFICATIONS_SETTINGS = {
        "FCM_API_KEY": "55076c5c84c03dff248a0b3245c2a18c9057116c",
        "GCM_API_KEY": "AIzaSyATLSjkTxT0HYOVv4FZ0L1-YagdVEU0UIQ",
        "APNS_CERTIFICATE": "/path/to/your/certificate.pem",
        "WP_POST_URL": {
        "CHROME": "https://chrome.example.com",
        "FIREFOX": "https://firefox.example.com",
        # Other browsers and their URLs
    },
}

ALLOWED_HOSTS = ["localhost:3000/","192.168.0.50"]

CORS_ALLOW_CREDENTIALS = True

# CORS_ORIGIN_WHITELIST = (
#     'http://localhost:3000',  # for localhost (REACT Default)
#     'http://192.168.0.50:3000',  # for network 
#     'http://localhost:8080',  # for localhost (Developlemt)
#     'http://192.168.0.50:8080',  # for network (Development)
# )

# CSRF_TRUSTED_ORIGINS = [
#     'http://localhost:3000',  # for localhost (REACT Default)
#     'http://192.168.0.50:3000',  # for network 
#     'http://localhost:8080',  # for localhost (Developlemt)
#     'http://192.168.0.50:8080',  # for network (Development)
# ]
CORS_ORIGIN_ALLOW_ALL = True
ALLOWED_HOSTS = ['*']
