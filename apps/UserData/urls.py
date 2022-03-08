from django.urls import path

from .views import UserProfilesView

app_name = 'UserData'
urlpatterns = [
    path('<pk>/pf/', UserProfilesView.as_view(), name = 'profile'),            
] 
