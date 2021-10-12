bind = '0.0.0.0:8000'
raw_env = [
   'DJANGO_SETTINGS_MODULE=Housing.settings'
]
user = 'adminswc'
group = 'adminswc'
backlog = 2048
workers = 3
accesslog = '/home/adminswc/BKHousing/logs/gunicorn.log'
errorlog = '/home/adminswc/BKHousing/logs/gunicorn.error.log'
capture_output = True
