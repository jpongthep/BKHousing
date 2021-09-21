from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django_pivot.pivot import pivot

from .models import RentPayment

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


