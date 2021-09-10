from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Unit


class UnitAdmin(admin.ModelAdmin):
    list_display = ['get_UnitGroup_display','ShortName', 'FullName']
    list_display_links = ['ShortName']
    search_fields = ('ShortName', 'FullName','username')
    ordering = ["UnitGroup", "id"]

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'CurrentUnit', 'FullName','MobilePhone', 'OfficePhone','last_login')
    ordering = ('-last_login','CurrentUnit','Rank',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', 
            {'fields': (
                    ('Rank', 'first_name', 'last_name'), 
                    ('BirthDay', 'PersonID'),
                    ('email', 'MobilePhone'),
                    ('current_status','current_spouse_name','current_spouse_pid'),
                    'Address'
                )
            }
        ),
        ('RTAF info', 
            {'fields': (
                        ('Position', 'CurrentUnit') ,
                        ('AFID', 'RTAFEMail', 'OfficePhone'),
                        ('current_salary','retire_date')

                    )
            }
        ),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),)

    add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')}),)
    list_filter = ('groups__name','CurrentUnit', 'Rank',)
    search_fields = ('first_name', 'last_name', 'CurrentUnit__ShortName','username','PersonID')

    # filter_horizontal = ('groups', 'user_permissions',)
    save_as = True


admin.site.register(User, UserAdmin)
admin.site.register(Unit, UnitAdmin)
