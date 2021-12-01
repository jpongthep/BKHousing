from django.urls import path, include

from .views import (ProcessFlow,
                    CreateHomeRequestView, 
                    UpdateHomeRequestView,
                    HomeRequestUnitListView,
                    HomeRequestAdminListView,
                    HomeRequestDetail,
                    HomeRequestUnitSummaryListView,
                    UnitList4PersonAdmin,
                    AFPersonListView,
                    update_process_step,
                    cancel_request,
                    homerequest_detail,
                    )

from .views_documents import (
                    TestDocument,
                    ConsentForm,
                    TestExcel,
                    UnitReportDocument,
                    line_notify,
                    download_decryp,
                    Excel4PersonAdmin
                    )
from .views_admin import (ManualCreateHomeRequestView,
                          ListHomeRequestView,
                          check_create_hr,
                          ManualHomeRequestAPIView,
                          ManualUpdateHomeRequestView,
                        )

from .views_modals import af_person_data_detailview
# from rest_framework import routers
# from .views import UnitList4PersonAdminViewSet

# router = routers.DefaultRouter()
# router.register(r'UnitList', UnitList4PersonAdminViewSet)

app_name = 'HomeRequest'
urlpatterns = [
    path('pf', ProcessFlow.as_view(), name = 'process_flow'),
    path('cr', CreateHomeRequestView.as_view(), name = 'create'),
    path('ml_sv', ManualHomeRequestAPIView.as_view(), name = 'manual_save'),
    path('ml_ck/<person_id>', check_create_hr, name = 'check_create'),
    path('ml/<person_id>', ManualCreateHomeRequestView.as_view(), name = 'manual'),
    path('ml_up/<pk>', ManualUpdateHomeRequestView.as_view(), name = 'manual_update'),
    path('mlls', ListHomeRequestView.as_view(), name = 'manual_list'),

    path('<pk>/ud', UpdateHomeRequestView.as_view(), name = 'update'),
    path('<pk>/dt', HomeRequestDetail.as_view(), name = 'detail'),
    path('afp', AFPersonListView.as_view(), name = 'af_person'),
    path('list', HomeRequestUnitListView.as_view(), name = 'list'),
    path('<unit_id>/list', HomeRequestUnitListView.as_view(), name = 'person_unit_list'),
    path('<unit_id>/mud', HomeRequestAdminListView.as_view(), name = 'modal_unit_data'),
    path('<unit_id>/fetch', UnitList4PersonAdmin.as_view(), name = 'unit_list_admin'),
    # api สำหรับการตรวจสอบความก้าวหน้า ขั้นตอนขอบ้าน ทาง App มือถือ
    path('cps/<str:username>/', homerequest_detail), # check process step
    path('lnfy/', line_notify, name = 'line_notify'), # check process step
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    path('ul', HomeRequestUnitSummaryListView.as_view(), name = 'unitlist'),
    path('<home_request_id>/<process_step>/ud',update_process_step, name = 'update_process_step'),
    path('<home_request_id>/hrc',cancel_request, name = 'cancel_request'),

    path('<pk>/md',af_person_data_detailview.as_view(), name = 'md'),

    path('ps_xls', Excel4PersonAdmin, name = 'xls_person_admin'),
    path('<unit_id>/xls', TestExcel, name = 'xls'),
    path('cf', ConsentForm, name = 'ConsentForm'),
    path('<home_request_id>/<detail_doc>/doc', TestDocument, name = 'detail_doc'),
    path('<home_request_id>/doc', TestDocument, name = 'doc'),
    path('<Unit_id>/doc_unit', UnitReportDocument, name = 'doc_unit'),
    path('dd/<hr_id>/<evidence>', download_decryp, name = 'download_decryp'),
] 
