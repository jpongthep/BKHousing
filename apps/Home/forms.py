from django import forms
from django.utils.translation import ugettext as _
from .models import CoResident, PetData, VehicalData


class CoResidentForm(forms.ModelForm):    
    class Meta:
        model = CoResident        
        fields = "__all__"
        # labels={                                            
        #         'full_name': _(u'คำนำหน้า ชื่อ นามสกุล'),                           
        #         'birth_day': _(u'วันเกิด (ใช้ปี ค.ศ.)'),
        #         # 'DELETE': _(u'ต้องการลบ ?'),
        #     }
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'คำนำหน้า ชื่อ นามสกุล'}),
            'birth_day': forms.DateInput(format=('%Y-%m-%d'),attrs={'type': 'date'}),
            'occupation': forms.TextInput(attrs={'placeholder': 'ระบุอาชีพ'}),
            'salary': forms.NumberInput(attrs={'value': '0'}),
        }

    def __init__(self,  *args, **kwargs):
        super(CoResidentForm, self).__init__(*args, **kwargs)                
        for name, field in self.fields.items():
            field.widget.attrs.update({'v-model': "co_resident." + name})        



class PetDataForm(forms.ModelForm):
    class Meta:
        model = PetData        
        fields = "__all__"
        # labels={                                            
        #         'full_name': _(u'คำนำหน้า ชื่อ นามสกุล'),                           
        #         'birth_day': _(u'วันเกิด (ใช้ปี ค.ศ.)'),
        #         # 'DELETE': _(u'ต้องการลบ ?'),
        #     }
        widgets = {
            'appearances': forms.Textarea(attrs={"rows":2, "cols":50})
        }

    def __init__(self,  *args, **kwargs):
        super(PetDataForm, self).__init__(*args, **kwargs)                
        for name, field in self.fields.items():
            field.widget.attrs.update({'v-model': "pet." + name})        




class VehicalDataForm(forms.ModelForm):
    class Meta:
        model = VehicalData        
        fields = "__all__"
        # labels={                                            
        #         'full_name': _(u'คำนำหน้า ชื่อ นามสกุล'),                           
        #         'birth_day': _(u'วันเกิด (ใช้ปี ค.ศ.)'),
        #         # 'DELETE': _(u'ต้องการลบ ?'),
        #     }


    def __init__(self,  *args, **kwargs):
        super(VehicalDataForm, self).__init__(*args, **kwargs)                
        for name, field in self.fields.items():
            field.widget.attrs.update({'v-model': "vehical." + name})        



            
