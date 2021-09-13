from django.contrib import admin
from django.db.models import Case, When, Count, Sum, Min, Max, IntegerField

from  apps.Payment.models import WaterPayment, RentPayment
from .models import HomeData, HomeOwner, CoResident, HomeOwnerSummary



@admin.register(HomeOwnerSummary)
class HomeOwnerSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/home_owner_summary_change_list.html'
    list_filter = ('owner__CurrentUnit__UnitGroup','owner__CurrentUnit__is_Bangkok')
    # date_hierarchy = 'created'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        OfficerRank = [30101 ,30102 ,30211 ,30212 ,30213 ,30221 ,30222 ,30231 ,30232 ,30301 ,30302 ,30411 ,30412 ,30421 ,30422 ,30431 ,30432 ,30511 ,30512 ,30521 ,30522 ,30531 ,30532 ,30541 ,30542 ,31411 ,31412 ,31421 ,31422 ,31431 ,31432 ,31511 ,31512 ,31521 ,31522 ,31531 ,31532]
        nonOfficerRank = [30611 ,30612 ,30711 ,30712 ,30721 ,30722 ,30731 ,30732 ,30811 ,30812 ,30821 ,30822 ,30831 ,30832 ,30841 ,30842]

        metrics = {
            'Number': Count('id'),
            'Officer' : Count(Case(When(owner__Rank__in = OfficerRank, then=1),output_field = IntegerField())),
            'nonOfficer' : Count(Case(When(owner__Rank__in = nonOfficerRank, then=1),output_field = IntegerField()))            
        }

        qs = qs.filter(is_stay = True
              ).values('owner__CurrentUnit','owner__CurrentUnit__UnitGroup', 'owner__CurrentUnit__ShortName'
              ).annotate(**metrics
              ).order_by('owner__CurrentUnit__id')

        response.context_data['summary'] = qs

        return response


class CoResidentInline(admin.TabularInline):
    model = CoResident
    extra = 3

    
@admin.register(HomeData)
class HomeDataAdmin(admin.ModelAdmin):
    list_filter = ('type', 'zone','status')
    search_fields = ['building_number','number']
    list_per_page = 30
    # list_display = ['year_round', 'FullName', 'Unit']
    # list_display_links = ['FullName']
    # save_as = True


class RentPaymentInline(admin.TabularInline):
    model = RentPayment
    exclude = ('comment',)
    max_num=0

    # def has_edit_permission(self, request, obj):
    #   return False
    # def has_add_permission(self, request, obj):
    #   return False
    # def has_delete_permission(self, request, obj=None):
    #     return False


@admin.register(HomeOwner)
class HomeOwnerAdmin(admin.ModelAdmin):
    list_display = ['is_stay','owner_unit','owner','home','lastest_command']
    list_display_links = ['owner']
    ordering = ('-is_stay','owner__Rank',)
    raw_id_fields = ('owner','home')
    list_filter = ('is_stay','home__zone','home__type','owner__CurrentUnit')
    search_fields = ['owner__first_name','home__number','home__number']
    inlines = [CoResidentInline,RentPaymentInline]

    def lastest_command(self, obj):
        if obj.is_stay:
            return f'เข้า {obj.enter_command}'
        else:
            return f'ออก {obj.leave_command}'
    lastest_command.short_description = 'คำสั่งล่าสุด'

    def owner_unit(self, obj):
        return obj.owner.CurrentUnit
    owner_unit.short_description = 'สังกัด'
    # search_fields = ['FullName',]
    # 
    # 
    # save_as = True
