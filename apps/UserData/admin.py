from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Unit


class UnitAdmin(admin.ModelAdmin):
    list_display = ['ShortName', 'FullName']
    
class UserAdmin(BaseUserAdmin):

    list_display = ('username', 'Unit', 'FullName','MobilePhone', 'OfficePhone')
    fieldsets = (
    (None, {'fields': ('username', 'password')}),
    ('Personal info', {'fields': (('Rank', 'first_name', 'last_name'), 'PersonID', 'email', 'MobilePhone')}),
    ('RTAF info', {'fields': (('Position', 'Unit') ,'AFID', 'RTAFEMail', 'OfficePhone')}),
    ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    ('Important dates', {'fields': ('last_login', 'date_joined')}),)

    add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')}),)
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'Unit__ShortName', 'email')
    ordering = ('Unit','username',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(User, UserAdmin)
admin.site.register(Unit, UnitAdmin)
