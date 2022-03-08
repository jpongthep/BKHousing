import datetime

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from .models import Feedback
# Create your views here.
class FeedbackCreate(LoginRequiredMixin, CreateView):
    login_url = '/login'
    model = Feedback
    template_name = "home.html"
    fields = ['text']
    success_url = reverse_lazy('Various:Thankyou')


    def get(self, *args, **kwargs):        
        if not (self.request.user.OfficePhone and self.request.user.MobilePhone) :
            messages.warning(self.request, 'กรุณากรอกข้อมูลเบอร์โทรศัพท์ และเบอร์มือถือให้เรียบร้อยก่อนดำเนินการต่อ')
            return redirect('UserData:profile', pk=self.request.user.id)        
        if self.request.user.OfficePhone == "-" and self.request.user.MobilePhone == "-" :
            messages.warning(self.request, 'กรุณากรอกข้อมูลเบอร์โทรศัพท์ และเบอร์มือถือให้เรียบร้อยก่อนดำเนินการต่อ')
            return redirect('UserData:profile', pk=self.request.user.id)        
        return super().get(self)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.commenter = self.request.user
        self.object.date = datetime.date.today()
        self.object.save()
        return super().form_valid(form)

class ThankyouTemplate(TemplateView):
    template_name = "Various/thankyou.html"
