from functools import reduce
from operator import or_

from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext
from django.db.models import Q

from django_admin_listfilter_dropdown.filters import (
    DropdownFilter, ChoiceDropdownFilter, RelatedDropdownFilter
)

from .models import HomeRequest, CoResident, HomeChange
from apps.UserData.models import User


class CoResidentInline(admin.TabularInline):
    model = CoResident
    extra = 1


class HomeRequestAdmin(admin.ModelAdmin):
    search_fields = ['FullName','Unit__ShortName']
    list_display = ['year_round', 'RequesterDateSend','modified','FullName', 'Unit','ProcessStep']
    list_filter = (
                    'year_round',
                    ('ProcessStep', ChoiceDropdownFilter),
                    ('Requester__CurrentUnit', RelatedDropdownFilter),
                )
    # date_hierarchy  = 'modified'
    list_display_links = ['FullName']
    raw_id_fields = ('Requester','UnitReciever', 'UnitApprover','PersonReciever','PersonApprover','recorder')
    ordering = ('-modified',)
    save_as = True

    actions = ['sendToStartProcess', 'sendOneStepBack', 'sendToUnitSendProcess']

    inlines = [CoResidentInline,]

    @admin.action(description='ย้อนไปขั้นตอนแรก (ผู้ขอแก้ไข)')
    def sendToStartProcess(self, request, queryset):
        updated = queryset.update(ProcessStep = 'RP',    RequesterDateSend = None, 
                                  UnitReciever = None,   UnitDateRecieved = None,
                                  UnitApprover = None,   cancel_request = False,
                                  PersonReciever = None, PersonDateRecieved = None,
                                  PersonApprover = None, PersonDateApproved = None,
                                  IsUnitEval = False,    UnitTroubleScore = None,
                                  IsPersonEval = False,  TroubleScore = None)
        self.message_user(request, ngettext('แก้ไขสถานะคำขอบ้าน %d คำขอเรียบร้อย','แก้ไขสถานะคำขอบ้าน %d คำขอเรียบร้อย',updated,) % updated, messages.SUCCESS)

    @admin.action(description='ย้อนไปขั้นตอน นขต.ส่งเรื่อง')
    def sendToUnitSendProcess(self, request, queryset):
        updated = queryset.filter(ProcessStep__in = ['PP','PA']
                         ).update(ProcessStep = 'US',    cancel_request = False,
                                  PersonReciever = None, PersonDateRecieved = None,
                                  PersonApprover = None, PersonDateApproved = None,                                    
                                  IsPersonEval = False)
        self.message_user(request, ngettext('แก้ไขสถานะคำขอบ้าน %d คำขอเรียบร้อย','แก้ไขสถานะคำขอบ้าน %d คำขอเรียบร้อย',updated,) % updated, messages.SUCCESS)
    
    @admin.action(description='ย้อนไปขั้นตอนก่อนหน้า')
    def sendOneStepBack(self, request, queryset):        
        updated = queryset.filter(ProcessStep = 'UP'
                         ).update(ProcessStep = 'RS',    cancel_request = False,
                                  UnitReciever = None,   UnitDateRecieved = None,
                                  IsUnitEval = False,    UnitTroubleScore = None,
                                  UnitApprover = None,   PersonReciever = None, 
                                  PersonDateRecieved = None,
                                  PersonApprover = None, PersonDateApproved = None,                                    
                                  IsPersonEval = False)
        updated = queryset.filter(ProcessStep = 'US'
                         ).update(ProcessStep = 'UP',    cancel_request = False,
                                  UnitApprover = None,   PersonReciever = None, 
                                  PersonDateRecieved = None,
                                  PersonApprover = None, PersonDateApproved = None,                                    
                                  IsPersonEval = False)
        self.message_user(request, ngettext('แก้ไขสถานะคำขอบ้าน %d คำขอเรียบร้อย','แก้ไขสถานะคำขอบ้าน %d คำขอเรียบร้อย',updated,) % updated, messages.SUCCESS)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "UnitReciever":
            kwargs["queryset"] = User.objects.filter(groups__name__in=['PERSON_SUBUNIT_ADMIN','PERSON_UNIT_ADMIN'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(HomeRequestAdmin, self).get_search_results(
                                               request, queryset, search_term)
        search_words = search_term.split()
        if search_words:
            q_objects = [Q(**{field + '__icontains': word}) for field in self.search_fields for word in search_words]
            queryset &= self.model.objects.filter(reduce(or_, q_objects))
        return queryset, use_distinct
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

class HomeChangeAdmin(admin.ModelAdmin):
    search_fields = ['FullName','Unit__ShortName']
    list_display = ['year_round', 'RequesterDateSend','modified','FullName', 'Unit','ProcessStep']
    list_filter = (
                    'year_round',
                    ('ProcessStep', ChoiceDropdownFilter),
                    ('Requester__CurrentUnit', RelatedDropdownFilter),
                )
    # date_hierarchy  = 'modified'
    list_display_links = ['FullName']
    raw_id_fields = ('Requester','current_home_owner', 'UnitReciever', 'UnitApprover','PersonReciever','PersonApprover','recorder')
    ordering = ('-modified',)
    save_as = True

admin.site.register(HomeChange, HomeChangeAdmin)
admin.site.register(HomeRequest, HomeRequestAdmin)


#สำหรับการอ้างอิงใน User model
class HomeRequestInline(admin.TabularInline):
    model = HomeRequest
    fk_name = "Requester"
    fields = ('year_round', 'Position', 'Unit','Status','num_children','RequesterDateSend','ProcessStep')
    ordering = ('-year_round',)
    extra = 0