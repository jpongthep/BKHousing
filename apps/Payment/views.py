from django.shortcuts import render
from django.views.generic import ListView

from django_pivot.pivot import pivot
from django_pivot.histogram import histogram

from .models import RentPayment

def RentPivot(request):
    queryset = RentPayment.objects.filter(home_owner__home__zone = '1'
                                 ).filter(home_owner__owner__Rank__lte = 30432
                                 ).order_by("home_owner__owner__Rank")
    print(queryset)
    pivot_table = pivot(queryset, 
                            [
                                'home_owner__home',
                                'home_owner__owner__Rank',
                                'home_owner__owner__first_name',
                                'home_owner__owner__last_name'
                            ], 
                            'date', 
                            'montly_bill'
                        )
    print(pivot_table)
    return render(request, "Payment/rent_list.html", {'pivot_data':pivot_table})

##https://github.com/martsberger/django-pivot
class RentListView(ListView):
    model = RentPayment
    template_name = "Payment/rent_list.html"
    ordering = ['-home_owner__owner__id']
    paginate_by = 50

