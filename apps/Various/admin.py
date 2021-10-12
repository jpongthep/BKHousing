from django.contrib import admin

from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    search_fields = ['home_owner__owner__FullName',]
    list_display = ['date','commenter','text']
    