from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth.forms import UserCreationForm

class MyAuthForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(MyAuthForm,self).__init__(*args, **kwargs)

    username = forms.CharField(
        widget=forms.TextInput(
            attrs = { 'autofocus': True,
                    'class' : 'form-control',
                    'id' : 'floatingInput',
                    'placeholder' : 'RTAF email account ไม่ต้องมี @rtaf.mi.th',
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

class MyLoginView(LoginView):    
    authentication_form = MyAuthForm
    # template_name = 'registration/login.html'
    # form_class = MyAuthForm