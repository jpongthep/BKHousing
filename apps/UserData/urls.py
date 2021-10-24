from django.urls import path

from .views import UpdateUserView, UserProfilesView

app_name = 'UserData'
urlpatterns = [
    path('<pk>/pf', UserProfilesView.as_view(), name = 'profile'),        
    path('<pk>/update', UpdateUserView.as_view(), name = 'update'),        
] 
