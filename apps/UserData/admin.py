from functools import reduce

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from operator import or_
from django.db.models import Q

from django_admin_listfilter_dropdown.filters import (
    DropdownFilter, ChoiceDropdownFilter, RelatedDropdownFilter
)

from .models import User, Unit
from apps.HomeRequest.admin import HomeRequestInline
from apps.Home.admin import HomeOwnerInline

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('assets/admin_userdata.css',)
        }
    list_display = ['get_UnitGroup_display','ShortName', 'FullName','sub_unit_list']
    list_display_links = ['ShortName']
    search_fields = ('ShortName', 'FullName')
    ordering = ["UnitGroup", "id"]

    # https://stackoverflow.com/questions/35796195/how-to-redirect-to-previous-page-in-django-after-post-request/35796330
    # https://stackoverflow.com/questions/17919361/how-can-i-add-a-button-into-django-admin-change-list-view-page/17921946
    change_form_template = "CustomAdmin/change_form.html"
    # change_list_template = "CustomAdmin/change_form.html"

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(UnitAdmin, self).get_fieldsets(request, obj)

        # print('self.media = ',self.media)
        return fieldsets

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'CurrentUnit','sub_unit', 'FullName','MobilePhone', 'OfficePhone','last_login')
    list_display_links = ['FullName']
    # date_hierarchy  = 'last_login'
    ordering = ('-last_login','CurrentUnit','Rank',)
    inlines = [HomeOwnerInline,HomeRequestInline]
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
                        ('Position', 'CurrentUnit','sub_unit') ,
                        ('AFID', 'RTAFEMail', 'OfficePhone'),
                        ('current_salary','retire_date')

                    )
            }
        ),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login','hris_update', 'date_joined')}),)

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
    list_filter = (
                    'groups__name',
                    'CurrentUnit__is_Bangkok',
                    ('CurrentUnit', RelatedDropdownFilter), 
                    ('Rank', ChoiceDropdownFilter)
                )
    search_fields = ('first_name', 'last_name', 'CurrentUnit__ShortName','username','PersonID')

    #  ('owner__CurrentUnit', RelatedDropdownFilter),
    # filter_horizontal = ('groups', 'user_permissions',)
    save_as = True

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(UserAdmin, self).get_fieldsets(request, obj)
        if request.user.groups.filter(name__in= self.limited_groups).exists():
            fieldsets = self.limited_fieldsets
        print('self.media = ',self.media)
        
        return fieldsets

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(UserAdmin, self).get_search_results(
                                               request, queryset, search_term)
        search_words = search_term.split()
        if search_words:
            q_objects = [Q(**{field + '__icontains': word}) for field in self.search_fields for word in search_words]
            queryset &= self.model.objects.filter(reduce(or_, q_objects))
        return queryset, use_distinct




