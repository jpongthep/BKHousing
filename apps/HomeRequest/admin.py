from django.contrib import admin
from .models import HomeRequest, CoResident

from apps.UserData.models import User


class CoResidentInline(admin.TabularInline):
    model = CoResident
    extra = 3

class HomeRequestAdmin(admin.ModelAdmin):
    search_fields = ['FullName',]
    list_display = ['year_round', 'FullName', 'Unit']
    list_display_links = ['FullName']
    raw_id_fields = ('Requester','UnitReciever', 'UnitApprover','PersonReciever','PersonApprover')
    save_as = True

    inlines = [CoResidentInline,]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "UnitReciever":
            kwargs["queryset"] = User.objects.filter(groups__name__in=['PERSON_UNIT_ADMIN'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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

admin.site.register(HomeRequest, HomeRequestAdmin)
