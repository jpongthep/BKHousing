from apps.HomeRequest.models import HomeRequest
from django.shortcuts import render
from django.views.generic import CreateView

from .models import HomeRequest

class CreateHomeRequestView(CreateView):
    model = HomeRequest
    fields = '__all__'
    template_name = "HomeRequest/CreateHomeRequest.html"
# Create your views here.
