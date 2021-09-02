from .settings import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'atkqueuedb',
        'username' : armis_user
        'PASSWORD' : '',
        'HOST' : 'localhost',
        'PORT' : '3306'  ,          
    }
}