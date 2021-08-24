
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from apps.UserData.views import MyLoginView
from django.contrib.auth.views import LogoutView
from .views import minView


urlpatterns = [
    # path('', blankView.as_view(), name = 'blank'),
    path('', minView.as_view(), name = 'blank'),

    path('login/', MyLoginView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(), name = 'logout'),

    path('hm/', include('apps.Home.urls')),
    path('hr/', include('apps.HomeRequest.urls')),
    path('pf/', include('apps.UserData.urls')),
    path('tr/', include('apps.Trouble.urls')),
    path('admin/', admin.site.urls),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
