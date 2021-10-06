import os

from .settings import *

DEBUG = True
ALLOWED_HOSTS = ['13.250.62.172','127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get("ARMIS_DB_NAME"),
        'HOST' : os.environ.get("ARMIS_DB_HOST"),
        'USER' : os.environ.get("ARMIS_DB_USER"),      
        'PASSWORD' : os.environ.get("ARMIS_DB_PASSWORD"),
        'PORT' : '3306' ,
        'OPTIONS': {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
