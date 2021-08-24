from django.contrib import admin

from .models import Command

class CommandAdmin(admin.ModelAdmin):
    pass
    # list_filter = ('type', 'zone','status')
    # search_fields = ['building_number','number']
    list_display = ['__str__', 'date_sign', 'date_effect','date_due','file']
    # list_display_links = ['FullName']
    # save_as = True



admin.site.register(Command, CommandAdmin)

