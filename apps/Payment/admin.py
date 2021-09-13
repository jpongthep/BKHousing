from django.contrib import admin

from .models import WaterPayment, RentPayment

@admin.register(WaterPayment)
class WaterPaymentAdmin(admin.ModelAdmin):
    raw_id_fields = ('home_owner',)
    date_hierarchy = 'date'

@admin.register(RentPayment)
class RentPaymentAdmin(admin.ModelAdmin):    
    raw_id_fields = ('home_owner',)
    date_hierarchy = 'date'
