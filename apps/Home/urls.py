from django.urls import path

from .views import (HomeOwnerUserDetailView, HomeDetailView,HomeOwnerDetailView)

app_name = 'HomeData'
urlpatterns = [
    path('<str:who>/dt', HomeOwnerUserDetailView.as_view(), name = 'detail_by_user'),
    path('<hm_id>/dt', HomeDetailView.as_view(), name = 'detail_home'),
    path('<hmowner_id>/hm_own', HomeOwnerDetailView.as_view(), name = 'owner_detail'),
] 
