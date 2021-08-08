from apps.HomeRequest.models import HomeRequest
from django.shortcuts import render
from django.views.generic import CreateView, ListView, DetailView

from .models import HomeRequest
from .forms import HomeRequestForm

class CreateHomeRequestView(CreateView):
    model = HomeRequest
    form_class = HomeRequestForm
    template_name = "HomeRequest/CreateHomeRequest.html"

class HomeRequestListView(ListView):
    model = HomeRequest    
    template_name = "HomeRequest/list.html"

class HomeRequestDetail(DetailView):
    model = HomeRequest
    template_name = "HomeRequest/Detail.html"

