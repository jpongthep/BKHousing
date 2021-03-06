from pathlib import Path
import os
import logging.config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-019j6f=&)joimhn(km7uakg_rj8u%c!&j-^+t7%77ql=jb2wqy"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # django APP
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # 3rd Party APP
    "crispy_forms",
    "crispy_bootstrap5", 
    'thaidate',
    'rest_framework',
    'django_admin_listfilter_dropdown',
    'django_crontab',

    # My Owner APP
    'apps.UserData',
    'apps.Home',
    'apps.Command',
    'apps.HomeRequest',
    'apps.Payment',
    'apps.Trouble',
    'apps.Configurations',
    'apps.Utility',
    'apps.Various',
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

ROOT_URLCONF = 'Housing.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'Housing.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'armis',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS':{
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'th'
TIME_ZONE = 'Asia/Bangkok'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/home'
LOGOUT_REDIRECT_URL = '/'
AUTHENTICATION_BACKENDS = [
                            'apps.UserData.AFAuthentications.SettingsBackend',
                            'django.contrib.auth.backends.ModelBackend'
                        ]

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_COOKIE_AGE = 2*60*60


AUTH_USER_MODEL = 'UserData.User'


STATIC_URL = '/static/'
# STATICFILES_DIRS = (os.path.join('static'),)
# STATIC_ROOT = '/static/'

# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'staticfiles',
]

MEDIA_URL = '/UploadFiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

CRONJOBS = [
    # ('*/5 * * * *', 'Housing.views.daily_notify_message')
    ('30 0 * * 1-5', 'apps.HomeRequest.views_notify.unit_daily_notify'),
]


DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname}-{asctime} : {module} [{message}]',
            'style': '{',
        },
        'simple': {
            'format': '{levelname}-{asctime} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'DebugFile': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'class': 'logging.FileHandler',
            'filename': 'logs/debug.log',
        },     
        'WarningFile': {
            'level': 'WARNING',
            'formatter': 'simple',
            'class': 'logging.FileHandler',
            'filename': 'logs/Warning.log',
        },     
        'LoginFile': {
            'level': 'DEBUG',
            'formatter': 'simple',
            'class': 'logging.FileHandler',
            'filename': 'logs/login.log',
        },     
        'EvidenceAccess': {
            'level': 'INFO',
            'formatter': 'simple',
            'class': 'logging.FileHandler',
            'filename': 'logs/EvidenceAccess.log',
        },     
        'adminFile': {
            'level': 'INFO',
            'formatter': 'simple',
            'class': 'logging.FileHandler',
            'filename': 'logs/admin.log',
        },     
    },
    'loggers': {
        'MainLog': {
            'handlers': ['DebugFile', 'WarningFile'],
            'level': 'DEBUG',
        },      
        'AdminLog': {
            'handlers': ['adminFile'],
            'level': 'DEBUG',
        },      
        'LoginLog': {
            'handlers': ['LoginFile'],
            'level': 'DEBUG',
        },      
        'EvidenceAccessLog': {
            'handlers': ['EvidenceAccess'],
            'level': 'INFO',
        },      
    }
}


logging.config.dictConfig(DEFAULT_LOGGING)