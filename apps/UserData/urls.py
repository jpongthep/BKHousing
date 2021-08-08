from django.urls import path

from .views import UpdateUserView

app_name = 'UserData'
urlpatterns = [
    path('<pk>/update', UpdateUserView.as_view(), name = 'update'),        
] 
