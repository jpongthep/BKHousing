from django import forms
from django.forms.fields import DateField
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext as _

from django.forms.widgets import Widget
from django.template import loader
from django.utils.safestring import mark_safe


from .models import HomeRequest, CoResident
from apps.Utility.Constants import HomeRentPermission


class UploadFileWidget(forms.FileInput):
    template_name = 'HomeRequest/upload_file_widget.html'

    def get_context(self, name, value, attrs=None):
        context = super().get_context(name, value, attrs)
        context['widget']['name'] = name
        context['widget']['value'] = value
        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class HomeRequestForm(forms.ModelForm):
    class Meta:
        model = HomeRequest
        fields = [
                'Rank' ,'FullName', 'Position', 'Unit',
                'Salary', 'AddSalary',
                'Status', 'SpouseName','SpousePID','SpouseAFID','IsHRISReport',
                'Address','GooglePlusCodes1',
                'TravelDescription',
                'RentPermission','RentStartDate','RentEndDate','RentOwner','RentOwnerPID','RentalCost',
                'RentAddress', 'GooglePlusCodes2',
                'IsNotBuyHome','IsNotOwnHome','IsNotRTAFHome','RTAFHomeLeaveReason','IsNeverRTAFHome',
                'IsHomelessDisaster','IsHomelessEvict','IsMoveFromOtherUnit','ImportanceDuty','OtherTrouble',
                'IsHomeNeed','IsFlatNeed','IsShopHouseNeed',
                'ZoneRequestPriority1','ZoneRequestPriority2','ZoneRequestPriority3','ZoneRequestPriority4','ZoneRequestPriority5','ZoneRequestPriority6',
                'HouseRegistration','DivorceRegistration','SpouseDeathRegistration','HomeRent6006','SpouseHomeRent6006','SalaryBill','SpouseApproved',
                ]        

        widgets = {
            'FullName': forms.TextInput(attrs = {'placeholder': 'น.อ.ทัพฟ้าไทย ใส่ใจการงาน'}),
            'Position': forms.TextInput(
                attrs={'placeholder': 'หัวหน้ากองสนับสนุนการบิน สำนักจัดการการบิน กรมการบินทหารอากาศ'}),
            'SubDistinct': forms.TextInput(
                attrs={
                    'placeholder': 'กรอกตำบลแล้วเลือก',
                }),
            
            'TravelDescription': forms.Textarea(
                attrs={
                        'placeholder': 'ในวันทำงานจะตื่นตั้งแต่ 0500 และปฏิบัติภารกิจส่วนตัว ออกจากบ้านเวลา 0540 แวะซื้อข้าวเพื่อทานเช้าและเที่ยง ถึงที่ทำงานเวลาประมาณ 0630',
                        'rows' : 4
                }),
            'OtherTrouble': forms.Textarea(
                attrs={
                        'placeholder': 'ความเดือดร้อนอื่น ๆ (ระบุ)',
                        'rows' : 2
                }),
            'RTAFHomeLeaveReason': forms.Textarea(
                attrs={
                        'placeholder': 'ข้อมูลบ้านพักหลังเดิมและสาเหตุการออก / ถูกไล่ออกโดยละเอียด',
                        'rows' : 2
                }),
            'RentStartDate' : forms.DateInput(format=('%Y-%m-%d'),attrs={'type': 'date'}),
            'RentEndDate' : forms.DateInput(format=('%Y-%m-%d'),attrs={'type': 'date'}),
            'RentPermission': forms.RadioSelect,
            'HouseRegistration' : UploadFileWidget(),
            'DivorceRegistration': UploadFileWidget(),
            'SpouseDeathRegistration': UploadFileWidget(),
            'HomeRent6006': UploadFileWidget(),
            'SpouseHomeRent6006': UploadFileWidget(),
            'SalaryBill': UploadFileWidget(),
            'SpouseApproved': UploadFileWidget(),
            'ZoneRequestPriority1' : forms.Select(attrs={'data-priority':'1'}),
            'ZoneRequestPriority2' : forms.Select(attrs={'data-priority':'2'}),
            'ZoneRequestPriority3' : forms.Select(attrs={'data-priority':'3'}),
            'ZoneRequestPriority4' : forms.Select(attrs={'data-priority':'4'}),
            'ZoneRequestPriority5' : forms.Select(attrs={'data-priority':'5'}),
            'ZoneRequestPriority6' : forms.Select(attrs={'data-priority':'6'}),
        }

    def __init__(self,  *args, **kwargs):
        super(HomeRequestForm, self).__init__(*args, **kwargs)
        self.fields['GooglePlusCodes1'].label = False
        self.fields['GooglePlusCodes2'].label = False        
        
        try:
            data = self.instance.Requester
            if data.Rank >= 30411:            
                self.fields['IsHomeNeed'].widget.attrs['disabled'] = True
                self.fields['IsHomeNeed'].label += " (เฉพาะนายพลอากาศ)"
            
            if data.current_status not in [2, 7]:            
                self.fields['IsShopHouseNeed'].widget.attrs['disabled'] = True
                self.fields['IsShopHouseNeed'].label += ' (เฉพาะผู้รายงานสภานภาพ "สมรส")'
        except:
            print("HomeRequest.forms : self.instance error ")


CoResidentFormSet = inlineformset_factory(HomeRequest,  # parent form
                                        CoResident,  # inline-form
                                        # inline-form fields
                                        fields=['PersonID', 'FullName','BirthDay','Relation','Occupation','Salary','Education'], 
                                        # fields=['PersonID', 'FullName','BirthDay','Relation','Occupation','Salary','Education'], 

                                        # labels for the fields
                                        labels={                                            
                                            'FullName': _(u'คำนำหน้า ชื่อ นามสกุล'),
                                        },
                                        widgets = {
                                            'BirthDay': forms.DateInput(
                                                    format=('%Y-%m-%d'),
                                                    attrs={
                                                        'placeholder': 'Select a date',
                                                        'type': 'date'
                                                        }),
                                            'PersonID': forms.TextInput(                                                    
                                                    attrs={
                                                        'placeholder': 'เลขประจำตัวประชาชน',
                                                        }),
                                        },

                                        # set to false because cant' delete an non-exsitant instance
                                        can_delete=True,

                                        # how many inline-forms are sent to the template by default
                                        extra = 1)


