from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Unit

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['get_UnitGroup_display','ShortName', 'FullName']
    list_display_links = ['ShortName']
    search_fields = ('ShortName', 'FullName','username')
    ordering = ["UnitGroup", "id"]

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'CurrentUnit', 'FullName','MobilePhone', 'OfficePhone','last_login')
    list_display_links = ['FullName']
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
    
    limited_groups = ['FINANCIAL_OFFICER', 'CIVIL_OFFICER']

    limited_fieldsets = (                
            ('Personal info', 
                {'fields': (
                        ('email', 'MobilePhone'),
                        ('Position', 'CurrentUnit') ,
                        ('AFID', 'RTAFEMail', 'OfficePhone')
                    )
                }
            ),)        
    list_filter = ('groups__name','CurrentUnit__is_Bangkok','CurrentUnit', 'Rank')
    search_fields = ('first_name', 'last_name', 'CurrentUnit__ShortName','username','PersonID')

    # filter_horizontal = ('groups', 'user_permissions',)
    save_as = True

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(UserAdmin, self).get_fieldsets(request, obj)
        if request.user.groups.filter(name__in= self.limited_groups).exists():
            fieldsets = self.limited_fieldsets
        
        return fieldsets




