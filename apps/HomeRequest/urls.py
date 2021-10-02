from django.urls import path, include

from .views import (ProcessFlow,
                    CreateHomeRequestView, 
                    UpdateHomeRequestView,
                    HomeRequestUnitListView,
                    HomeRequestAdminListView,
                    HomeRequestDetail,
                    HomeRequestUnitSummaryListView,
                    TestDocument,
                    TestExcel,
                    UnitList4PersonAdmin,
                    AFPersonListView,
                    update_process_step,
                    cancel_request)

from .views_modals import af_person_data_detailview
# from rest_framework import routers
# from .views import UnitList4PersonAdminViewSet

# router = routers.DefaultRouter()
# router.register(r'UnitList', UnitList4PersonAdminViewSet)

app_name = 'HomeRequest'
urlpatterns = [
    path('pf', ProcessFlow.as_view(), name = 'process_flow'),
    path('cr', CreateHomeRequestView.as_view(), name = 'create'),
    path('<pk>/ud', UpdateHomeRequestView.as_view(), name = 'update'),
    path('<pk>/dt', HomeRequestDetail.as_view(), name = 'detail'),
    path('afp', AFPersonListView.as_view(), name = 'af_person'),
    path('list', HomeRequestUnitListView.as_view(), name = 'list'),
    path('<unit_id>/list', HomeRequestUnitListView.as_view(), name = 'person_unit_list'),
    path('<unit_id>/mud', HomeRequestAdminListView.as_view(), name = 'modal_unit_data'),
    path('<unit_id>/fetch', UnitList4PersonAdmin.as_view(), name = 'unit_list_admin'),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    path('ul', HomeRequestUnitSummaryListView.as_view(), name = 'unitlist'),
    path('<home_request_id>/<process_step>/ud',update_process_step, name = 'update_process_step'),
    path('<home_request_id>/hrc',cancel_request, name = 'cancel_request'),

    path('<pk>/md',af_person_data_detailview.as_view(), name = 'md'),

    path('<unit_id>/xls', TestExcel, name = 'xls'),
    path('<home_request_id>/doc', TestDocument, name = 'doc'),
] 
