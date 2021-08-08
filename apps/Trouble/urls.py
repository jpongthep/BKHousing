
from django.urls import path


from .views import Evaluation



app_name = 'Trouble'
urlpatterns = [
    path('<int:HomeRequstID>/<str:Type>/eval',Evaluation, name = 'eval'),
]
