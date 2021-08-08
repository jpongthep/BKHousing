from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import TemplateView

class BlankView(TemplateView):
    template_name = "_minbase.html"

urlpatterns = [
    path('', BlankView.as_view(), name = 'blank'),

    path('hr/', include('apps.HomeRequest.urls')),

    path('admin/', admin.site.urls),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
