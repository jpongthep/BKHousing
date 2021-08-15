from django.shortcuts import render
from django.views.generic import DetailView

from .models import HomeData, HomeOwner

class HomeDetailView(DetailView):
    model = HomeData
    template_name = "Home/detail.html"

class HomeOwnerDetailView(DetailView):
    model = HomeOwner
    template_name = "Home/hm_own_detail.html"
