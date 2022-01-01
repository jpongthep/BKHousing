
from django.urls import path


from .views import Evaluation, view_eval, PersonEvaluation, UnitEvaluation



app_name = 'Trouble'
urlpatterns = [
    path('<int:HomeRequstID>/<str:Type>/eval',Evaluation, name = 'eval'),
    path('<int:HomeRequstID>/ue',UnitEvaluation, name = 'unit_evaluation'),
    path('<int:HomeRequstID>/pe',PersonEvaluation, name = 'person_evaluation'),
    path('<int:HomeRequstID>/<str:eval_type>/view_eval',view_eval, name = 'view_eval'),
]
