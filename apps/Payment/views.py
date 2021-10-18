from datetime import date, timedelta
import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from django_pivot.pivot import pivot

from apps.HomeRequest.views import AuthenUserTestMixin
from .models import RentPayment, FinanceData
from .serializers import FinanceDataSerializer
from apps.Utility.Constants import FINANCE_CODE

##https://github.com/martsberger/django-pivot
@login_required
def RentPivot(request):
    queryset = RentPayment.objects.order_by("home_owner__owner__Rank")
    page = request.GET.get('page', 1)
    # print(queryset)
    pivot_list = pivot(queryset, 
                            [
                                'home_owner__home',
                                'home_owner__owner__Rank',
                                'home_owner__owner__first_name',
                                'home_owner__owner__last_name'
                            ], 
                            'date', 
                            'montly_bill'
                        )
    # print(pivot_list)
    paginator = Paginator(pivot_list, 50)
    try:
        pivot_table = paginator.page(page)
    except PageNotAnInteger:
        pivot_table = paginator.page(1)
    except EmptyPage:
        pivot_table = paginator.page(paginator.num_pages)
    return render(request, "Payment/rent_list.html", {'pivot_data':pivot_table})

class GetRent(AuthenUserTestMixin, APIView):
    allow_groups = ['RTAF_NO_HOME_USER', 'RTAF_HOME_USER']

    def get(self, request, **kwargs):
        person_id = kwargs["person_id"]
        print('person_id = ',person_id)   

        queryset =  FinanceData.objects.filter(PersonID =  person_id
                                      ).filter(date__gte = date.today() - timedelta(days = 185)
                                      ).filter(code = FINANCE_CODE.HOMERENT
                                      ).filter(money__gt = 0
                                      ).order_by("money")
        if queryset.exists():
            money = queryset[0].money
        else:
            money = 0

        dump = json.dumps({'money': money})            
        return HttpResponse(dump, content_type='application/json')