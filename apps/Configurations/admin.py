from django.contrib import admin
from apps.Configurations.models import YearRound

class YearRoundAdmin(admin.ModelAdmin):
    list_display = ['__str__','Step1', 'Step2', 'Step3', 'CurrentStep']
    list_editable = ['CurrentStep']
    search_fields = ['Year']
    ordering = ["Year", "Round"]
    
admin.site.register(YearRound, YearRoundAdmin)
