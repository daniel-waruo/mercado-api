"""
Django settings for root project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import django_heroku

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/
import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# reading .env file
environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = []

if DEBUG:
    ALLOWED_HOSTS.append("*")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # custom applications
    'products',
    'buyers',
    'orders',
    'ussd',
    'screens',
    'm_sessions',
    'whatsapp',
    'payments',
    'gas_screens'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'root.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'gas_screens/templates')],
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

WSGI_APPLICATION = 'root.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

# set screen urls path
SCREEN_URLS_PATH = 'gas_screens.screen_urls'

# africastalking configuration
AFRICASTALKING = {
    'username': env('AT_USERNAME'),
    'api_key': env('AT_API_KEY'),
    'product_name': env('AT_PRODUCT_NAME')
}

# MPESA CONFIGURATIONS
# credentials needed for payment
DARAJA_CONFIG = {
    "short_code": os.environ.get("DARAJA_SHORT_CODE"),
    "consumer_key": os.environ.get("DARAJA_CONSUMER_KEY"),
    "consumer_secret": os.environ.get("DARAJA_CONSUMER_SECRET"),
    "pass_key": os.environ.get("DARAJA_PASS_KEY")
}

# this is the base url for the daraja website
DARAJA_BASE_URL = os.environ.get("DARAJA_URL")

# this is the callback base url for the daraja callback
CALLBACK_BASE_URL = os.environ.get("CALLBACK_BASE_URL")

# default vendor config
VENDOR = {
    'phone': env('VENDOR_PHONE'),
    'name': env('VENDOR_NAME')
}

# WABA CREDENTIALS
WABA_API_KEY = env.str("WABA_API_KEY")


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Activate django heroku settings
django_heroku.settings(locals())
