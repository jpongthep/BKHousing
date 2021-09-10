from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['*','ec2-54-151-164-105.ap-southeast-1.compute.amazonaws.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'armis_db',
	    'HOST' : 'aws-mysqlhunterdogdb.cevi5wuglaux.ap-southeast-1.rds.amazonaws.com',
        'USER' : 'armis_user',        
        'PASSWORD' : 'YD$^55#r@deN',
        'PORT' : '3306' ,
        'OPTIONS': {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
