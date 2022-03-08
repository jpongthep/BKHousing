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
from apps.Home.models import HomeOwner
from apps.Home.modules import MoveFromHomeRequest
from apps.HomeRequest.views_notify import unit_new_allocate_notify

                                     

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


#สำหรับการอ้างอิงใน User model
class HomeRequestInline(admin.TabularInline):
    model = HomeRequest
    fk_name = "Requester"
    fields = ('year_round', 'Position', 'Unit','Status','num_children','RequesterDateSend','ProcessStep')
    ordering = ('-year_round',)
    extra = 0


class HomeRequestAllocate(HomeRequest):
    class Meta:
        verbose_name_plural = "HomeRequestAllocate : จัดสรรบ้านให้คำขอใหม่"
        proxy = True

class HomeRequestAllocateAdmin(admin.ModelAdmin):
    search_fields = ['FullName','Unit__ShortName']
    list_display = ['year_round', 'FullName', 'Unit','request_type','home_allocate','enter_command','published','make_contract']
    list_editable = ('home_allocate','enter_command')
    list_filter = (
                    ('ProcessStep', ChoiceDropdownFilter),
                    ('Requester__CurrentUnit', RelatedDropdownFilter),
                    ('enter_command', RelatedDropdownFilter),
                    'published',
                    'make_contract'
                )
    # date_hierarchy  = 'modified'
    list_per_page = 100
    list_display_links = ['FullName']
    raw_id_fields = ('home_allocate','enter_command')
    ordering = ('-modified',)
    change_list_template = "HomeRequest/CustomAdmin/change_list_template.html"

    def get_queryset(self, request):
        return self.model.objects.filter(Q(ProcessStep = 'PP') | Q(ProcessStep = 'PA')  | Q(ProcessStep = 'GH'))


    actions = ['publish_allocate',]

    inlines = [CoResidentInline,]

    @admin.action(description='ประกาศการจัดสรรบ้านพัก')
    def publish_allocate(self, request, queryset):
        has_error = 0
        for qs in queryset:
            user = qs.Requester

            # if qs.published:
            #     messages.warning(request,f"ประกาศ {qs.Requester.FullName} ซ้ำ ข้ามการประกาศ")
            #     continue 

            
            if not qs.home_allocate:
                messages.warning(request,f"ยังไม่บันทึกการจัดสรรบ้านของ {qs.Requester.FullName}")
                has_error += 1
            
            if not qs.enter_command:
                messages.warning(request,f"ยังไม่บันทึกคำสั่งบ้านของ {qs.Requester.FullName}")
                has_error += 1        
            
            if has_error > 0:
                break

            home_owner = HomeOwner.objects.filter(owner = user                                         
                                         ).filter(is_stay = True)

            if home_owner.exists():
                home_owner[0].is_stay = False
                home_owner[0].save()
                messages.warning(request,f"ย้าย {qs.Requester.FullName} ออกจากบ้านพักหลังเดิม และย้ายเข้าหลังใหม่แล้ว")
                # has_error += 1
        
        if has_error > 0:
            messages.error(request,f"ไม่สามารถประกาศผลการจัดสรรได้ ตรวจสอบ / บันทึกข้อมูลก่อนประกาศ")
            return

        # if not qs.published:
        updated = queryset.update(ProcessStep = 'GH', lastest_allocate = True, published = True)
        for qs in queryset:
            MoveFromHomeRequest(qs)
        # unit_new_allocate_notify(request)
        self.message_user(request, ngettext('ประกาศการจัดสรรบ้าน %d หลัง','ประกาศการจัดสรรบ้าน %d หลัง',updated,) % updated, messages.SUCCESS)



admin.site.register(HomeChange, HomeChangeAdmin)
admin.site.register(HomeRequest, HomeRequestAdmin)
admin.site.register(HomeRequestAllocate, HomeRequestAllocateAdmin)