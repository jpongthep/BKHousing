from django.urls import path

from .views import (ProcessFlow,
                    CreateHomeRequestView, 
                    UpdateHomeRequestView,
                    HomeRequestUnitListView,
                    HomeRequestDetail,
                    HomeRequestUnitSummaryListView,
                    TestDocument,
                    TestExcel,
                    AFPersonListView,
                    update_process_step)

from .views_modals import af_person_data_detailview
app_name = 'HomeRequest'
urlpatterns = [
    path('pf', ProcessFlow.as_view(), name = 'process_flow'),
    path('cr', CreateHomeRequestView.as_view(), name = 'create'),
    path('<pk>/ud', UpdateHomeRequestView.as_view(), name = 'update'),
    path('<pk>/dt', HomeRequestDetail.as_view(), name = 'detail'),
    path('afp', AFPersonListView.as_view(), name = 'af_person'),
    path('list', HomeRequestUnitListView.as_view(), name = 'list'),
    path('<unit_id>/list', HomeRequestUnitListView.as_view(), name = 'person_unit_list'),
    path('<unit_id>/mud', HomeRequestUnitListView.as_view(), name = 'model_unit_data'),
    
    path('ul', HomeRequestUnitSummaryListView.as_view(), name = 'unitlist'),
    path('<home_request_id>/<process_step>/ud',update_process_step, name = 'update_process_step'),

    path('<pk>/md',af_person_data_detailview.as_view(), name = 'md'),

    path('<unit_id>/xls', TestExcel, name = 'xls'),
    path('<home_request_id>/doc', TestDocument, name = 'doc'),
] 
