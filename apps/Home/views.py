import json

from django.shortcuts import render
from django.views.generic import DetailView
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from .models import HomeData, HomeOwner
from apps.HomeRequest.models import HomeChange
from apps.HomeRequest.forms_homechange import HomeChangeBlankForm
from apps.UserData.models import User
from apps.Payment.models import WaterPayment, RentPayment
from .serializers import HomeOwnerSerializer


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
        rent_payments = RentPayment.objects.filter(home_owner = home_owner).order_by("-date")
        water_payments = WaterPayment.objects.filter(home_owner = home_owner).order_by("-date")
        context['rent_payments'] = rent_payments
        context['water_payments'] = water_payments
        context['home_change_form'] = HomeChangeBlankForm(
                                            home_owner = HomeOwner.objects.get(id = home_owner), 
                                            user = self.request.user)

        return context

class HomeOwnerDetailView(DetailView):
    model = HomeOwner
    template_name = "Home/hm_own_detail.html"


@csrf_exempt
def homeowner_api(request, username):
    message = 'only post method with secure code'

    if request.method == 'POST':
        body = json.loads(request.body)
        if body["key"] == "123":
            try:
                user = User.objects.get(username = username)             
                homeowner = HomeOwner.objects.filter(owner = user).filter(is_stay = True)
            except User.DoesNotExist:
                dump = json.dumps({'status': 'username not found'})            
                return HttpResponse(dump, content_type='application/json')

            if not homeowner.exists():
                dump = json.dumps({'status': 'home not found'})            
                return HttpResponse(dump, content_type='application/json')
            serializer = HomeOwnerSerializer(homeowner[0])
            return JsonResponse(serializer.data)
        else:
            message = f"wrong secure code {request.body}"

    dump = json.dumps({'status': message})            
    return HttpResponse(dump, content_type='application/json')

