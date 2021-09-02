from .settings import *

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'ec2-54-151-164-105.ap-southeast-1.compute.amazonaws.com']
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'atkqueuedb',
        'username' : 'armis_user'
        'PASSWORD' : '',
        'HOST' : 'localhost',
        'PORT' : '3306'  ,          
    }
}