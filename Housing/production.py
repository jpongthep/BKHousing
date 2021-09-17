import os

from .settings import *

DEBUG = True
ALLOWED_HOSTS = ['*','ec2-54-151-164-105.ap-southeast-1.compute.amazonaws.com']

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
