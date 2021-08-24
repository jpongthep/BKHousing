from django.apps import AppConfig


class HomerequestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.HomeRequest'
    verbose_name = "คำร้องขอเข้าพักอาศัย"

    # def ready(self): #method just to import the signals
    # 	import apps.HomeRequest.signals