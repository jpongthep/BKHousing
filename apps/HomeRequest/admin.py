from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext

from .models import HomeRequest, CoResident
from apps.UserData.models import User


class CoResidentInline(admin.TabularInline):
    model = CoResident
    extra = 3


class HomeRequestAdmin(admin.ModelAdmin):
    search_fields = ['FullName',]
    list_display = ['year_round', 'created', 'FullName', 'Unit','ProcessStep']
    list_filter = ('year_round','Requester__CurrentUnit')
    list_display_links = ['FullName']
    raw_id_fields = ('Requester','UnitReciever', 'UnitApprover','PersonReciever','PersonApprover')
    save_as = True
    actions = ['sendToStartProcess']

    inlines = [CoResidentInline,]

    @admin.action(description='ย้อนไปขั้นตอนแรก (ผู้ขอแก้ไข)')
    def sendToStartProcess(self, request, queryset):
        updated = queryset.update(ProcessStep = 'RP',    RequesterDateSend = None, 
                                    UnitReciever = None,   UnitDateRecieved = None,
                                    UnitApprover = None,   cancel_request = False,
                                    PersonReciever = None, PersonDateRecieved = None,
                                    PersonApprover = None, PersonDateApproved = None,
                                    IsUnitEval = False,    UnitTroubleScore = None,
                                    IsPersonEval = False,   TroubleScore = None)
        self.message_user(request, ngettext('แก้ไขสถานะคำขอบ้าน %d คำขอเรียบร้อย','แก้ไขสถานะคำขอบ้าน %d คำขอเรียบร้อย',updated,) % updated, messages.SUCCESS)

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
