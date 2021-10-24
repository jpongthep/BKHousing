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
                    'placeholder' : 'RTAF email',
                    'size' : 20}))
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


                  
class UserCurrentDataForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['OfficePhone', 'MobilePhone','RTAFEMail', 'email']
        
        widgets = {
            'OfficePhone': forms.TextInput(attrs = {'placeholder': 'x-xxxx'}),
            'MobilePhone': forms.TextInput(attrs={'placeholder': 'xx xxxx xxxx'}),
            'RTAFEMail': forms.EmailInput(),
            'email': forms.EmailInput(),
        }
    def __init__(self, *args, **kwargs):
        super(UserCurrentDataForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = "ที่อยู่ email อื่น ๆ"

