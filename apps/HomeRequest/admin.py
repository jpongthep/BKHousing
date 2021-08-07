from django.contrib import admin
from .models import HomeRequest, CoResident


class CoResidentInline(admin.TabularInline):
    model = CoResident
    extra = 3

class HomeRequestAdmin(admin.ModelAdmin):
    search_fields = ['FullName',]
    list_display = ['YearRound', 'FullName', 'Unit']
    inlines = [CoResidentInline,]
    # fieldsets = (
    #     ('Standard info', {
    #         'fields': (
    #                     ('Rank','FullName'),
    #                     ('AFID','PersonID'),
    #                     'Position', 
    #                 )
    #     }),
    #     ('Address info', {
    #         'fields': (
                        
    #                     ('Address','SubDistinct','Distinct','Province','GooglePlusCodes1'),
    #                     'TravelDescription'

    #                 )
    #     }),
    # )

# class HomeRequestAdmin(admin.ModelAdmin):
#     pass
    # list_display = ['YearRound', 'FullName', 
    #                 'Affiliation', 'FormStatus', 'ProcedureStatus','TroubleEvaulatePerson','TroubleEvaulateUnit']
    # search_fields = ['FullName']
    # list_display_links = ['FullName']
    # list_editable = ['FormStatus','ProcedureStatus','TroubleEvaulatePerson','TroubleEvaulateUnit']


    # list_filter = ['Type']
    # list_editable = ['Type','NumDay']
    # list_display_links = ['Person']
admin.site.register(HomeRequest, HomeRequestAdmin)
