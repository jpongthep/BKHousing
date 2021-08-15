from django.apps import AppConfig


class HomerequestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.HomeRequest'

    # def ready(self): #method just to import the signals
    # 	import apps.HomeRequest.signals