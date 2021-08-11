from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import TemplateView

class minView(TemplateView):
    template_name = "_minbase.html"

class blankView(TemplateView):
    template_name = "_blank.html"

urlpatterns = [
    path('', blankView.as_view(), name = 'blank'),
    path('min', minView.as_view(), name = 'blank'),

    path('hr/', include('apps.HomeRequest.urls')),
    path('pf/', include('apps.UserData.urls')),
    path('tr/', include('apps.Trouble.urls')),
    path('admin/', admin.site.urls),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
