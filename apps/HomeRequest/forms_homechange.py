from django.contrib import admin
admin.autodiscover()

from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

from apps.Home.models import HomeData
from apps.HomeRequest.models import HomeChange
# from apps.Home.models import HomeOwner
from apps.UserData.models import User

class HomeChangeBlankForm(forms.ModelForm):
    class Meta:
        model = HomeChange
        # new_home = forms.ModelChoiceField(queryset=HomeData.objects.all(), widget=forms.TextInput)
        fields = '__all__'
        exclude = ['Rank', 'FullName','cancel_request','UnitReciever','UnitDateRecieved','UnitApprover',
                   'UnitDateApproved','PersonReciever','PersonDateRecieved','PersonApprover',
                   'PersonDateApproved','foster_person','foster_date','foster_reason','have_document',
                   'document_number','document_date','created','modified']

    def __init__(self, home_owner, user,  *args, **kwargs):
        super(HomeChangeBlankForm, self).__init__(*args, **kwargs)

        self.fields['Requester'].queryset = User.objects.filter(id = user.id)
        self.fields['Requester'].initial = user.id
        self.fields['recorder'].queryset = User.objects.filter(id = user.id)
        self.fields['recorder'].initial = user.id
        self.fields['current_home_owner'].queryset = User.objects.filter(id = home_owner.owner.id)
        self.fields['current_home_owner'].initial = home_owner.owner.id
       
        self.fields['Unit'].widget = forms.TextInput()
        self.fields['new_home'].widge = forms.TextInput()
       
        self.fields['swap_home_owner'].widget = forms.TextInput()
        self.fields['change_comment'].widget = forms.Textarea(attrs={'cols': 10, 'rows': 3})
        self.fields['recorder'].label = ""
        # for name, field in self.fields.items():
        #     field.widget.attrs.update({'v-model': "homechange_form." + name})            

        # self.fields['budget_year'].widget = forms.HiddenInput()

