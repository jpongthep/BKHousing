
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from apps.UserData.views import MyLoginView
from apps.Various.views import FeedbackCreate
from django.contrib.auth.views import LogoutView
from .views import LandingTemplate


admin.site.site_header = 'ARMIS Admin site'
admin.site.index_title = 'ฐานข้อมูลหลังบ้าน'
admin.site.site_title = 'หน้าหลัก'
admin.site.site_url = '/home'

urlpatterns = [
    path('', LandingTemplate.as_view(), name = 'ldn'),
    path('home', FeedbackCreate.as_view(), name = 'Home'),

    path('login/', MyLoginView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(), name = 'logout'),

    path('hm/', include('apps.Home.urls')),
    path('pm/', include('apps.Payment.urls')),
    path('hr/', include('apps.HomeRequest.urls')),
    path('us/', include('apps.UserData.urls')),
    path('tr/', include('apps.Trouble.urls')),     
    path('fb/', include('apps.Various.urls')),     
    path('admin/', admin.site.urls),

] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
