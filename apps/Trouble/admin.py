from django.contrib import admin
from .models import (SetForm, 
                     Question,
                     QuestionList, 
                     Choices,
                     FilledForm,
                     AnsweredForm)

class QuestionListInline(admin.TabularInline):
    model = QuestionList
    extra = 0

class SetFormAdmin(admin.ModelAdmin):
    inlines = [QuestionListInline,]

class ChoicesInline(admin.TabularInline):
    model = Choices
    extra = 0

class QuestionAdmin(admin.ModelAdmin):    
    inlines = [ChoicesInline,]

class AnsweredFormInline(admin.TabularInline):
    model = AnsweredForm
    extra = 1

class FilledFormAdmin(admin.ModelAdmin):
    search_fields = ['HomeRequestForm__FirstName', 'HomeRequestForm__LastName']
    inlines = [AnsweredFormInline,]

admin.site.register(SetForm, SetFormAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(FilledForm, FilledFormAdmin)