import os

from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['*','ec2-54-151-164-105.ap-southeast-1.compute.amazonaws.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get("DB_NAME"),
        'HOST' : os.environ.get("DB_HOST"),
        'USER' : os.environ.get("DB_USER"),      
        'PASSWORD' : os.environ.get("DB_PASSWORD"),
        'PORT' : '3306' ,
        'OPTIONS': {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
