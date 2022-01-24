from django.urls import path

from .views import (HomeOwnerUserDetailView, 
                    HomeDetailView,
                    HomeOwnerDetailView,
                    homeowner_api)
from .views_api import HomeOwnerViewSet, CoResidentViewSet

app_name = 'HomeData'
urlpatterns = [
    path('<str:who>/dt', HomeOwnerUserDetailView.as_view(), name = 'detail_by_user'),
    path('<hm_id>/dt', HomeDetailView.as_view(), name = 'detail_home'),
    path('<hmowner_id>/hm_own', HomeOwnerDetailView.as_view(), name = 'owner_detail'),
    path('<username>/hm_own_api', homeowner_api, name = 'hm_own_api'),

    path('hm_own_new_api', HomeOwnerViewSet.as_view(), name = 'hm_own_new_api'),
    path('cs_api', CoResidentViewSet.as_view(), name = 'coresident_api'),
] 
