from django.urls import path

from .views import (CreateHomeRequestView, 
                    UpdateHomeRequestView,
                    HomeRequestUnitListView,
                    HomeRequestDetail,
                    HomeRequestUnitSummaryListView,
                    TestDocument,
                    TestExcel,
                    AFPersonListView)

app_name = 'HomeRequest'
urlpatterns = [
    path('cr', CreateHomeRequestView.as_view(), name = 'create'),
    path('<pk>/ud', UpdateHomeRequestView.as_view(), name = 'update'),
    path('<pk>/dt', HomeRequestDetail.as_view(), name = 'detail'),
    path('afp', AFPersonListView.as_view(), name = 'af_person'),
    path('list', HomeRequestUnitListView.as_view(), name = 'list'),
    path('<unit_id>/list', HomeRequestUnitListView.as_view(), name = 'person_unit_list'),
    path('ul', HomeRequestUnitSummaryListView.as_view(), name = 'unitlist'),

    path('<unit_id>/xls', TestExcel, name = 'xls'),
    path('<home_request_id>/doc', TestDocument, name = 'doc'),
] 
