from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext as _


from .models import HomeRequest, CoResident

class HomeRequestForm(forms.ModelForm):
    class Meta:
        model = HomeRequest
        fields = ['Rank' ,'FullName', 'Position', 'Salary', 'AddSalary', 'HouseRegistration','HomeRent6006']
        # fileds = '__all__'
        # exclude = ['Requester', 'DateSend', 'YearRound', 'UnitApprover', 
        #            'PersonApprover', 'IsTroubleSelf', 'IsTroubleUnit', 'IsTroublePerson']
        widgets = {
            'FullName': forms.TextInput(attrs = {'placeholder': 'น.อ.ทัพฟ้าไทย ใส่ใจการงาน'}),
            'Position': forms.TextInput(
                attrs={'placeholder': 'หัวหน้ากองสนับสนุนการบิน สำนักจัดการการบิน กรมการบินทหารอากาศ'}),
            'TravelDescription': forms.Textarea(
                attrs={
                        'placeholder': 'ในวันทำงานจะตื่นตั้งแต่ 0500 และปฏิบัติภารกิตส่วนตัว ออกจากบ้านเวลา 0540 แวะซื้อข้าวเพื่อทานเช้าและเที่ยง ถึงที่ทำงานเวลาประมาณ 0630',
                        'rows' : 4
                }),
        }


CoResidentFormSet = inlineformset_factory(HomeRequest,  # parent form
                                        CoResident,  # inline-form
                                        # inline-form fields
                                        fields=['PersonID', 'FullName','BirthDay','Relation'], 
                                        # fields=['PersonID', 'FullName','BirthDay','Relation','Occupation','Salary','Education'], 

                                        # labels for the fields
                                        labels={
                                            'PersonID': _(u'PersonID'),
                                            'FullName': _(u'คำนำหน้า ชื่อ นามสกุล'),
                                        },

                                        # set to false because cant' delete an non-exsitant instance
                                        can_delete=False,

                                        # how many inline-forms are sent to the template by default
                                        extra = 3)
