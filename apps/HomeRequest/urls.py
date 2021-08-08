from django.urls import path

from .views import (CreateHomeRequestView, HomeRequestListView,HomeRequestDetail)

app_name = 'HomeRequest'
urlpatterns = [
    path('create', CreateHomeRequestView.as_view(), name = 'create'),
    path('<pk>/detail', HomeRequestDetail.as_view(), name = 'detail'),
    path('list', HomeRequestListView.as_view(), name = 'list'),
    
] 
