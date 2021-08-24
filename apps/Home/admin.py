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
    raw_id_fields = ('owner','home')
    list_filter = ('is_stay','home__zone','home__type','owner__CurrentUnit')
    search_fields = ['owner__first_name','home__number','home__number']
    inlines = [CoResidentInline,]
    # search_fields = ['FullName',]
    # list_display = ['year_round', 'FullName', 'Unit']
    # list_display_links = ['FullName']
    # save_as = True


admin.site.register(HomeData, HomeDataAdmin)
admin.site.register(HomeOwner, HomeOwnerAdmin)
# Register your models here.
