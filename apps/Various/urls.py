from django.urls import path

from .views import ThankyouTemplate

app_name = 'Various'
urlpatterns = [
    path('thx', ThankyouTemplate.as_view(), name = 'Thankyou'),
] 
