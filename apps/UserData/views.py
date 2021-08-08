from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import UpdateView

from .models import User
from .forms import MyAuthForm, UserForm


class MyLoginView(LoginView):    
    authentication_form = MyAuthForm


class UpdateUserView(UpdateView):
    model = User
    form_class = UserForm
    template_name = "UserData/UpdateUser.html"

