from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import UpdateView, TemplateView


from .models import User
from .forms import MyAuthForm, UserForm


class MyLoginView(LoginView):    
    authentication_form = MyAuthForm
    template_name = 'registration/new_login.html'


class UserProfilesView(TemplateView):
    template_name = "UserData/profile.html"

class UpdateUserView(UpdateView):
    model = User
    form_class = UserForm
    template_name = "UserData/UpdateUser.html"

