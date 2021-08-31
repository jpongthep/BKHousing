from django.contrib import admin
from .models import HomeData, HomeOwner, CoResident


class CoResidentInline(admin.TabularInline):
    model = CoResident
    extra = 3

    

class HomeDataAdmin(admin.ModelAdmin):
    list_filter = ('type', 'zone','status')
    search_fields = ['building_number','number']
    list_per_page = 30
    # list_display = ['year_round', 'FullName', 'Unit']
    # list_display_links = ['FullName']
    # save_as = True

class HomeOwnerAdmin(admin.ModelAdmin):
    list_display = ['is_stay','owner_unit','owner','home','lastest_command']
    list_display_links = ['owner']
    ordering = ('-is_stay','owner__Rank',)
    raw_id_fields = ('owner','home')
    list_filter = ('is_stay','home__zone','home__type','owner__CurrentUnit')
    search_fields = ['owner__first_name','home__number','home__number']
    inlines = [CoResidentInline,]

    def lastest_command(self, obj):
        if obj.is_stay:
            return obj.enter_command
        else:
            return obj.leave_command
    lastest_command.short_description = 'คำสั่งล่าสุด'

    def owner_unit(self, obj):
        return obj.owner.CurrentUnit
    owner_unit.short_description = 'สังกัด'
    # search_fields = ['FullName',]
    # 
    # 
    # save_as = True


admin.site.register(HomeData, HomeDataAdmin)
admin.site.register(HomeOwner, HomeOwnerAdmin)
# Register your models here.
