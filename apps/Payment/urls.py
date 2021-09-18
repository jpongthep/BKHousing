from django.urls import path

from .views import RentPivot

app_name = 'Payment'
urlpatterns = [
    path('rent', RentPivot, name = 'RentList'),
   
] 
