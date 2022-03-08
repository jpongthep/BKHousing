import io

from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext as _

from django.template import loader
from django.utils.safestring import mark_safe

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

from .models import HomeRequest, CoResident
from apps.UserData.forms import UserCurrentDataForm
from apps.Utility.utils import encryp_file


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
                'Rank' ,'FullName', 'Position', 'Unit', 'sub_unit',
                'Salary', 'AddSalary',
                'Status', 'SpouseName','SpousePID','spouse_office','SpouseAFID','num_children','num_study_children', 'IsHRISReport',
                'Address','GooglePlusCodes1','distance',
                'work_commute','TravelDescription',
                'RentPermission','have_rent', 'have_rent_spouse', 'RentalCost', 'RentalCostSpouse', 'rent_comment',
                'IsNotBuyHome','IsNotOwnHome','IsNotRTAFHome','RTAFHomeLeaveReason','IsNeverRTAFHome',
                'IsHomelessDisaster','ContinueHouse', 'IsHomelessEvict','IsMoveFromOtherUnit','ImportanceDuty','OtherTrouble',
                'IsHomeNeed','IsFlatNeed','IsShopHouseNeed',
                'ZoneRequestPriority1','ZoneRequestPriority2','ZoneRequestPriority3','ZoneRequestPriority4','ZoneRequestPriority5','ZoneRequestPriority6',
                'HouseRegistration', 'MarriageRegistration', 'SpouseApproved', 'DivorceRegistration','SpouseDeathRegistration',
                ]        

        widgets = {
            'FullName': forms.TextInput(attrs = {'placeholder': 'น.อ.ทัพฟ้าไทย ใส่ใจการงาน'}),
            'Position': forms.TextInput(
                attrs={'placeholder': 'หก.กอษ.กกศ.สนผ.กบ.ทอ.'}),
                        
            'GooglePlusCodes1': forms.TextInput(attrs={'placeholder': 'WJFC+9P Bangkok, Thailand'}),

            'Salary': forms.NumberInput(attrs={ 'min': 0,
                                                'step':1,
                                                'onkeypress' : "return event.charCode >= 48 && event.charCode <= 57"
                                                }),

            'distance': forms.NumberInput(attrs={ 'min': 0,
                                                  'step':1,
                                                  'onkeypress' : "return event.charCode >= 48 && event.charCode <= 57"
                                                }),
                        
            'TravelDescription': forms.Textarea(
                attrs={ 'placeholder': 'เขียนอธิบายการเดินทางไป - กลับในแต่ละวันตั้งแต่เวลาตื่นตอนเช้าจนถึงเวลากลับบ้าน เวลาออกจากบ้าน เวลาถึงบ้าน ระยะทาง ระยะเวลาที่ใช้เดินทาง ภารกิจที่ต้องทำในแต่ละวัน เช่น การส่ง-รับลูก การดูแลพ่อแม่ หรือภารกิจของหน่วยที่ทำให้ต้องมาก่อน / เลิกหลังเวลา...',
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
            'HouseRegistration' : UploadFileWidget(),
            'MarriageRegistration': UploadFileWidget(),
            'DivorceRegistration': UploadFileWidget(),
            'SpouseDeathRegistration': UploadFileWidget(),
            'SpouseApproved': UploadFileWidget(),
            'RentPermission' : forms.Select(attrs={'class':'mt-2'}),
            'rent_comment': forms.Textarea(
                attrs={
                        'placeholder': 'ชี้แจงเพิ่มเติมถึงสาเหตุ/เหตุผลพิเศษ เกี่ยวกับ คชบ.',
                        'rows' : 3,
                        'class' : "mt-2"
                }),
            'ZoneRequestPriority1' : forms.Select(attrs={'data-priority':'1'}),
            'ZoneRequestPriority2' : forms.Select(attrs={'data-priority':'2'}),
            'ZoneRequestPriority3' : forms.Select(attrs={'data-priority':'3'}),
            'ZoneRequestPriority4' : forms.Select(attrs={'data-priority':'4'}),
            'ZoneRequestPriority5' : forms.Select(attrs={'data-priority':'5'}),
            'ZoneRequestPriority6' : forms.Select(attrs={'data-priority':'6'}),
        }
        # labels = {
        #     'RentStartDate': _(u'วันเริ่มสัญญาเช่าบ้าน (ใช้ปี ค.ศ.)'),
        #     'RentEndDate': _(u'วันสิ้นสุดสัญญาเช่าบ้าน (ใช้ปี ค.ศ.)'),
        # }

    def __init__(self,  *args, **kwargs):
        super(HomeRequestForm, self).__init__(*args, **kwargs)
        self.fields['GooglePlusCodes1'].label = False
        self.fields['RentalCost'].label = False
        self.fields['RentalCostSpouse'].label = False

        for name, field in self.fields.items():
            # add ng-model to each model field
            ng_model_prefix = getattr(self,  'hr', '')
            ng_model = '{}{}'.format(ng_model_prefix, name)
            field.widget.attrs.setdefault('hr', ng_model)
        
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


    def encryp_file_field(self, upload_file):
        # data = self.cleaned_data['HouseRegistration']
        data = upload_file

        # ถ้าไม่ได้แก้ไขไฟล์เข้ารหัสเดิม ก็ไม่ต้องทำอะไร
        if ".enc" in data.name and data.name[-4:] == ".pdf":
            return data

        file_data = data.read()
        encryp_data = encryp_file(file_data)

        # data.write(encryp_data)
        # print('HouseRegistration = ', data)
        data.size = len(encryp_data)
        
        data.name = data.name[:-4] + ".enc.pdf"
        # print('data.name  =', data.name)

        data.file  = io.BytesIO(encryp_data)

        return data

    def clean(self):
        cleaned_data = self.cleaned_data

        cleaned_data['HouseRegistration'] = self.encryp_file_field(cleaned_data['HouseRegistration']) if cleaned_data['HouseRegistration'] else None
        cleaned_data['MarriageRegistration'] = self.encryp_file_field(cleaned_data['MarriageRegistration']) if cleaned_data['MarriageRegistration'] else None
        cleaned_data['SpouseApproved'] = self.encryp_file_field(cleaned_data['SpouseApproved']) if cleaned_data['SpouseApproved'] else None
        cleaned_data['DivorceRegistration'] = self.encryp_file_field(cleaned_data['DivorceRegistration']) if cleaned_data['DivorceRegistration'] else None
        cleaned_data['SpouseDeathRegistration'] = self.encryp_file_field(cleaned_data['SpouseDeathRegistration']) if cleaned_data['SpouseDeathRegistration'] else None

        return cleaned_data 


class ManualHomeRequestForm(forms.ModelForm):
    class Meta:
        model = HomeRequest
        fields = ['Requester','year_round', 'FullName', 'Position', 'Unit', 'Address', 'Salary',
                'RentPermission', 'RentalCost','Status', 'IsHRISReport', 'IsNotBuyHome', 
                'IsNotOwnHome', 'ContinueHouse', 'IsMoveFromOtherUnit', 'IsUnitEval','UnitTroubleScore','IsPersonEval','PersonTroubleScore',
                'ImportanceDuty','OtherTrouble', 'Comment', 'request_type', 'IsHomeNeed', 'IsFlatNeed', 'IsShopHouseNeed', 
                'ZoneRequestPriority1','ZoneRequestPriority2',
                'specificed_need', 'foster_person', 'foster_date', 'foster_reason', 'have_document', 
                'document_number', 'document_date','ProcessStep'
                ]
        widgets = {
            'Requester': forms.TextInput(attrs = {'class': 'd-none'}),
            'year_round': forms.TextInput(attrs = {'class': 'd-none'}),
            'OtherTrouble': forms.Textarea(attrs={'rows' : 2}),
            'Comment': forms.Textarea(attrs={'rows' : 2}),
            'foster_date': forms.DateInput(format=('%Y-%m-%d'),attrs={'type': 'date'}),
            'document_date': forms.DateInput(format=('%Y-%m-%d'),attrs={'type': 'date'}),
        }


class CrispyManualHomeRequestForm(ManualHomeRequestForm): #,UserCurrentDataForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('Requester', css_class='d-none form-group col-md-4 mb-0 hidden'),
                Column('year_round', css_class='d-none form-group col-md-2 mb-0'),

                css_class='form-row'
            ),
            Row(
                Column('FullName', css_class='form-group col-md-4 mb-0'),
                Column('Position', css_class='form-group col-md-6 mb-0'),
                Column('Unit', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            # Row(
            #     Column('UserCurrentDataForm', css_class='form-group col-md-3 mb-0'),
            #     Column('MobilePhone', css_class='form-group col-md-3 mb-0'),
            #     Column('RTAFEMail', css_class='form-group col-md-3 mb-0'),
            #     Column('email', css_class='form-group col-md-3 mb-0'),
            #     css_class='form-row'
            # ),
            Row(
                Column('Address', css_class='form-group col-md-5 mb-0'),
                Column('RentPermission', css_class='form-group col-md-2 mb-0'),
                Column('RentalCost', css_class='form-group col-md-2 mb-0'),
                Column('Status', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('IsHRISReport', css_class='form-group col-md-2 mb-0'),
                Column('IsNotBuyHome', css_class='form-group col-md-2 mb-0'),
                Column('IsNotOwnHome', css_class='form-group col-md-2 mb-0'),
                Column('ContinueHouse', css_class='form-group col-md-2 mb-0'),
                Column('IsMoveFromOtherUnit', css_class='form-group col-md-2 mb-0'),
                Column('ImportanceDuty', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('OtherTrouble', css_class='form-group col-md-6 mb-0'),
                Column('Comment', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('IsUnitEval', css_class='form-group col-md-2 mb-0'),
                Column('UnitTroubleScore', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),

            Row(
                Column('request_type', css_class='form-group col-md-2 mb-0'),
                Column('IsHomeNeed', css_class='form-group col-md-2 mb-0'),
                Column('IsFlatNeed', css_class='form-group col-md-2 mb-0'),
                Column('IsShopHouseNeed', css_class='form-group col-md-2 mb-0'),                
                Column('ZoneRequestPriority1', css_class='form-group col-md-2 mb-0'),                
                Column('ZoneRequestPriority2', css_class='form-group col-md-2 mb-0'),                
                css_class='form-row'
            ),
            Row(
                Column('specificed_need', css_class='form-group col-md-4 mb-0'),
                Column('foster_person', css_class='form-group col-md-2 mb-0'),
                Column('foster_date', css_class='form-group col-md-2 mb-0'),                
                Column('foster_reason', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('have_document', css_class='form-group col-md-2 mb-0'),
                Column('document_number', css_class='form-group col-md-2 mb-0'),
                Column('document_date', css_class='form-group col-md-2 mb-0'),
                Column('ProcessStep', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'บันทึกข้อมูล')
        )



CoResidentFormSet = inlineformset_factory(HomeRequest,  # parent form
                                          CoResident,  # inline-form
                                        # inline-form fields
                                        fields=['PersonID', 'FullName','BirthDay','Relation','Occupation','Salary','Education'], 
                                        # fields=['PersonID', 'FullName','BirthDay','Relation','Occupation','Salary','Education'], 

                                        # labels for the fields
                                        labels={                                            
                                            'FullName': _(u'คำนำหน้า ชื่อ นามสกุล'),                           
                                            'BirthDay': _(u'วันเกิด (ใช้ปี ค.ศ.)'),
                                            # 'DELETE': _(u'ต้องการลบ ?'),
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


