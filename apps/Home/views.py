from django.shortcuts import render
from django.views.generic import DetailView
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import HomeData, HomeOwner
from apps.UserData.models import User
from apps.Payment.models import WaterPayment, RentPayment


class HomeDetailView(DetailView):
    model = HomeData
    template_name = "Home/detail.html"

class HomeOwnerUserDetailView(LoginRequiredMixin, DetailView):
    model = HomeOwner
    template_name = "Home/detail_by_user.html"
    login_url = '/login' 

    def get(self, request, *args, **kwargs):

        if 'who' in self.kwargs:
            who = self.kwargs['who']
        try:
            if who == 'spouse':
                spouse = User.objects.get(id = request.user.id)
                user = User.objects.get(current_spouse_pid = spouse.PersonID)
            elif who == 'owner':
                user = User.objects.get(id = request.user.id)
            else:
                raise Http404()
        except User.DoesNotExist :
            raise Http404()

        home_data = HomeOwner.objects.filter(owner = user).order_by("-is_stay")

        self.object = home_data
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        home_owner = context["object"][0].id
        rent_payments = RentPayment.objects.filter(home_owner = home_owner)
        water_payments = WaterPayment.objects.filter(home_owner = home_owner)
        context['rent_payments'] = rent_payments
        context['water_payments'] = water_payments

        return context

class HomeOwnerDetailView(DetailView):
    model = HomeOwner
    template_name = "Home/hm_own_detail.html"
