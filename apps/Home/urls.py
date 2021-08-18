from django.urls import path

from .views import (HomeDetailView,HomeOwnerDetailView)

app_name = 'HomeData'
urlpatterns = [
    path('<hm_id>/dt', HomeDetailView.as_view(), name = 'detail'),
    path('<hmowner_id>/hm_own', HomeOwnerDetailView.as_view(), name = 'owner_detail'),
] 
