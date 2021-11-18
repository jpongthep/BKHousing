from datetime import date, timedelta

from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import UpdateView, TemplateView
from django.urls import reverse
from django.contrib import messages

from .models import User
from apps.Payment.models import FinanceData
from .forms import MyAuthForm, UserCurrentDataForm

from apps.Utility.Constants import FINANCE_CODE

class MyLoginView(LoginView):    
    authentication_form = MyAuthForm
    template_name = 'registration/new_login.html'


class UserProfilesView(UpdateView):
    model = User
    form_class = UserCurrentDataForm
    template_name = "UserData/profile.html"

    def get_success_url(self):
        return reverse('UserData:profile', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        homerent_data = FinanceData.objects.filter(PersonID =  self.request.user.PersonID
                                          ).filter(date__gte = date.today() - timedelta(days = 185)
                                          ).filter(code = FINANCE_CODE.HOMERENT
                                          ).filter(money__gt = 0
                                          ).order_by("money","-date")
        if homerent_data.exists():
            data['rent'] = homerent_data[0].money
            data['rent_month'] = homerent_data[0].date
        else:
            data['rent'] = 0
        return data    

    def post(self, request, *args, **kwargs):
        messages.success(request,'บันทึกการแก้ไขเรียบร้อย')
        return super().post(request, *args, **kwargs)

