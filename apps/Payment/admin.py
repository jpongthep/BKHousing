from django.contrib import admin

from .models import WaterPayment, RentPayment

@admin.register(WaterPayment)
class WaterPaymentAdmin(admin.ModelAdmin):
    search_fields = ['home_owner__owner__FullName',]
    raw_id_fields = ('home_owner',)
    date_hierarchy = 'date'
    

@admin.register(RentPayment)
class RentPaymentAdmin(admin.ModelAdmin):  
    search_fields = ['home_owner__owner__first_name','home_owner__owner__last_name']
    raw_id_fields = ('home_owner',)
    date_hierarchy = 'date'
    



