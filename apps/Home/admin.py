from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db import models
from django.db.models import Case, When, Count, Sum, Min, Max, IntegerField
from django.forms import TextInput, Textarea, Select

from django_admin_listfilter_dropdown.filters import (
    DropdownFilter, ChoiceDropdownFilter, RelatedDropdownFilter
)

from  apps.Payment.models import WaterPayment, RentPayment
from .models import HomeData, HomeOwner, CoResident, HomeOwnerSummary, PetData, VehicalData



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

class PetDataInline(admin.TabularInline):
    model = PetData
    extra = 2
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':20})},
        models.PositiveIntegerField: {'widget': TextInput(attrs={'size':'8'})},
        models.DecimalField: {'widget': TextInput(attrs={'size':'8'})},
        models.TextField: {'widget': Textarea(attrs={'rows' : 2, 'cols':30})},
        models.ForeignKey: {'widget': Select(attrs={'style': 'width: 250px;'})},
    } 

class VehicalDataInline(admin.TabularInline):
    model = VehicalData
    extra = 2


class BuildingFilter(SimpleListFilter):
    title = "???????????????"  # a label for our filter
    parameter_name = "building_number"  # you can put anything here

    def lookups(self, request, model_admin):
        return [(i,i) for i in range(1,17)]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        if queryset.model is HomeData:
            return queryset.filter(building_number=self.value())
        if queryset.model is HomeOwner:
            return queryset.filter(home__building_number=self.value())


@admin.register(CoResident)
class CoResidentAdmin(admin.ModelAdmin):
    search_fields = ['full_name', 'person_id']
    list_per_page = 30
    list_display = ['person_id','full_name', 'relation','age','home_owner']
    
    list_display_links = ['full_name']
    # save_as = True

@admin.register(VehicalData)
class VehicalDataAdmin(admin.ModelAdmin):
    search_fields = ['plate', 'province']
    list_per_page = 30
    list_display = ['plate', 'province','type', 'brand','color','home_parker']
    
    list_display_links = ['plate']
    # save_as = True

@admin.register(HomeData)
class HomeDataAdmin(admin.ModelAdmin):
    list_filter = (
                    ('type',ChoiceDropdownFilter), 
                    ('zone',ChoiceDropdownFilter),
                    BuildingFilter,
                    ('status',ChoiceDropdownFilter),
                    )
    search_fields = ['type', 'building_number','room_number', 'number']
    list_per_page = 30
    list_display = ['__str__', 'building_number','room_number', 'electric_meter_number','electric_meter_amp','electric_meter_line','status']
    list_editable = ['electric_meter_number','electric_meter_amp','electric_meter_line',]

    list_display_links = ['__str__']
    # save_as = True


class WaterPaymentInline(admin.TabularInline):
    model = WaterPayment
    exclude = ('PersonID', 'comment',)
    ordering = ['-date',]
    max_num=0

    # def has_edit_permission(self, request, obj):
    #   return False
    # def has_add_permission(self, request, obj):
    #   return False
    # def has_delete_permission(self, request, obj=None):
    #     return False

class RentPaymentInline(admin.TabularInline):
    model = RentPayment
    exclude = ('PersonID', 'comment',)
    ordering = ['-date',]
    max_num = 0

    # def has_edit_permission(self, request, obj):
    #   return False
    # def has_add_permission(self, request, obj):
    #   return False
    # def has_delete_permission(self, request, obj=None):
    #     return False


#?????????????????????????????????????????????????????? User model
class HomeOwnerInline(admin.TabularInline):
    model = HomeOwner
    exclude = ('insurance_rate','rent_rate','water_meter_insurance','water_meter','electric_meter',)
    extra = 0

@admin.register(HomeOwner)
class HomeOwnerAdmin(admin.ModelAdmin):
    list_display = ['is_stay','owner_unit','owner','home','home_type','home_zone','lastest_command', 'leave_command']
    list_editable  = ['is_stay','leave_command']
    list_display_links = ['owner']
    ordering = ('-enter_command__year','-enter_command__number')
    raw_id_fields = ('owner','home','leave_command')
    list_filter = (
                    'is_stay',
                    ('enter_command',RelatedDropdownFilter),
                    ('leave_command',RelatedDropdownFilter),
                    ('home__type',ChoiceDropdownFilter), 
                    ('home__zone',ChoiceDropdownFilter),
                    BuildingFilter,
                    ('owner__CurrentUnit', RelatedDropdownFilter),
                  )
    search_fields = ['owner__first_name','owner__last_name','home__number','enter_command__year']
    inlines = [CoResidentInline, PetDataInline, VehicalDataInline, RentPaymentInline, WaterPaymentInline]

    def get_queryset(self, request):
        qs = super(HomeOwnerAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.groups.filter(name = 'PERSON_UNIT_ADMIN').exists():
            return qs.filter(owner__CurrentUnit = request.user.CurrentUnit)
        elif request.user.groups.filter(name = 'PERSON_SUBUNIT_ADMIN').exists():
            return qs.filter(owner__sub_unit = request.user.sub_unit)
        else:
            return qs

    def lastest_command(self, obj):
        from django.utils.html import format_html
        if obj.is_stay:
            text = f"<b>???????????????????????? {obj.enter_command}</b>" if obj.enter_command else "-"
            return format_html(text)
        else:
            return format_html("<font style = 'color:rgb(160, 160, 160);'>????????????????????? {}</font>", obj.leave_command)
            
    lastest_command.short_description = '????????????????????????????????????'

    def owner_unit(self, obj):
        return obj.owner.CurrentUnit
    owner_unit.short_description = '??????????????????'

    def home_type(self, obj):
        return obj.home.get_type_display()
    home_type.short_description = '??????????????????'

    def home_zone(self, obj):
        return obj.home.get_zone_display()
    home_zone.short_description = '??????????????????????????????'

    def get_inlines(self, request, obj):
        inlines = super(HomeOwnerAdmin, self).get_inlines(request, obj)
        if request.user.groups.filter(name__in= ['FINANCIAL_OFFICER']).exists():
            inlines = [RentPaymentInline]
        elif request.user.groups.filter(name__in= ['CIVIL_OFFICER']).exists():
            inlines = [WaterPaymentInline]
        
        return inlines
    # search_fields = ['FullName',]
    # 
    # 
    # save_as = True
