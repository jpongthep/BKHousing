from django.urls import path

from .views import (HomeOwnerUserDetailView, 
                    HomeDetailView,
                    HomeOwnerDetailView,
                    homeowner_api,
                    ContractFormDocument)
from .views_api import HomeOwnerViewSet, CoResidentViewSet,VehicalDataViewSet, PetDataViewSet

app_name = 'HomeData'
urlpatterns = [
    path('<str:who>/dt', HomeOwnerUserDetailView.as_view(), name = 'detail_by_user'),
    path('<hm_id>/dt', HomeDetailView.as_view(), name = 'detail_home'),
    path('<hmowner_id>/hm_own', HomeOwnerDetailView.as_view(), name = 'owner_detail'),
    path('<username>/hm_own_api', homeowner_api, name = 'hm_own_api'),

    path('hm_own_new_api', HomeOwnerViewSet.as_view(), name = 'hm_own_new_api'),
    path('cs_api', CoResidentViewSet.as_view(), name = 'coresident_api'),
    path('cs_api/<pk>', CoResidentViewSet.as_view(), name = 'coresident_api'),
    path('vd_api', VehicalDataViewSet.as_view(), name = 'vehical_api'),
    path('vd_api/<pk>', VehicalDataViewSet.as_view(), name = 'vehical_api'),
    path('pd_api', PetDataViewSet.as_view(), name = 'pet_api'),
    path('pd_api/<pk>', PetDataViewSet.as_view(), name = 'pet_api'),
    path('cfd/<home_data_id>', ContractFormDocument, name = 'ContractFormDocument'),
] 
