import os

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import FileResponse

class minView(LoginRequiredMixin,TemplateView):
    login_url = '/login'
    template_name = "_minbase.html"

