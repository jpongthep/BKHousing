from django.urls import path

from .views import CreateHomeRequestView

urlpatterns = [
    path('create', CreateHomeRequestView.as_view(), name = 'createHomeRequest'),
    
] 
