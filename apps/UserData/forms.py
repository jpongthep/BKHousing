from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth.forms import UserCreationForm

from .models import User

class MyAuthForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(MyAuthForm,self).__init__(*args, **kwargs)

    username = forms.CharField(
        widget=forms.TextInput(
            attrs = { 'autofocus': True,
                    'class' : 'form-control',
                    'id' : 'floatingInput',
                    'placeholder' : 'RTAF email ไม่ต้องมี @rtaf.mi.th',
                    'size' : 30}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'current-password',
                    'class' : 'form-control',
                    'placeholder' : 'password',
                    'id' : 'floatingPassword'                                    
                    })
    )


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields =  ['Rank','first_name', 'last_name', 'email', 
                  'PersonID', 'AFID', 'Position', 'CurrentUnit', 'OfficePhone',
                  'MobilePhone', 'RTAFEMail' ]
                  

