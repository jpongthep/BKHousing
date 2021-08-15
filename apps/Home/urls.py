from django.urls import path

from .views import (HomeDetailView,HomeOwnerDetailView)

app_name = 'HomeData'
urlpatterns = [
    path('<pk>/dt', HomeDetailView.as_view(), name = 'detail'),
    path('<pk>/hm_own', HomeOwnerDetailView.as_view(), name = 'owner_detail'),
] 
