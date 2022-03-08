from django.urls import path

from .views import RentPivot, GetRent

app_name = 'Payment'
urlpatterns = [
    path('rent/', RentPivot, name = 'RentList'),
    path('<str:person_id>/gr/', GetRent.as_view(), name = 'GetRent'),
] 
