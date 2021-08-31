from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext as _


from .models import HomeRequest, CoResident
from apps.Utility.Constants import HomeRentPermission


class HomeRequestForm(forms.ModelForm):
    class Meta:
        model = HomeRequest
        fields = [
                'Rank' ,'FullName', 'Position', 'Unit',
                'Salary', 'AddSalary',
                'Status', 'SpouseName','SpousePID','SpouseAFID','IsHRISReport',
                'Address','SubDistinct','Distinct','Province','GooglePlusCodes1',
                'TravelDescription',
                'RentPermission','RentStartDate','RentEndDate','RentOwner','RentOwnerPID','RentalCost',
                'RentAddress', 'RentSubDistinct', 'RentDistinct', 'RentProvince', 'GooglePlusCodes2',
                'IsNotBuyHome','IsNotOwnHome','IsNotRTAFHome','RTAFHomeLeaveReason','IsNeverRTAFHome',
                'IsHomelessDisaster','IsHomelessEvict','IsMoveFromOtherUnit','ImportanceDuty','OtherTrouble',
                'IsHomeNeed','IsFlatNeed','IsShopHouseNeed',
                'ZoneRequestPriority1','ZoneRequestPriority2','ZoneRequestPriority3','ZoneRequestPriority4','ZoneRequestPriority5','ZoneRequestPriority6',
                'HouseRegistration','DivorceRegistration','SpouseDeathRegistration','HomeRent6006','SpouseHomeRent6006','SalaryBill','SpouseApproved',
                ]        
        # exclude = ['Requester', 'DateSend', 'YearRound', 'UnitApprover', 
        #            'PersonApprover', 'IsTroubleSelf', 'IsTroubleUnit', 'IsTroublePerson']
        
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
                        'placeholder': 'ในวันทำงานจะตื่นตั้งแต่ 0500 และปฏิบัติภารกิตส่วนตัว ออกจากบ้านเวลา 0540 แวะซื้อข้าวเพื่อทานเช้าและเที่ยง ถึงที่ทำงานเวลาประมาณ 0630',
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
            'RentPermission': forms.RadioSelect,
            'HouseRegistration' : forms.FileInput(attrs={'accept':'application/pdf'}),
            'DivorceRegistration': forms.FileInput(attrs={'accept':'application/pdf'}),
            'SpouseDeathRegistration': forms.FileInput(attrs={'accept':'application/pdf'}),
            'HomeRent6006': forms.FileInput(attrs={'accept':'application/pdf'}),
            'SpouseHomeRent6006': forms.FileInput(attrs={'accept':'application/pdf'}),
            'SalaryBill': forms.FileInput(attrs={'accept':'application/pdf'}),
            'SpouseApproved': forms.FileInput(attrs={'accept':'application/pdf'}),                
        }


CoResidentFormSet = inlineformset_factory(HomeRequest,  # parent form
                                        CoResident,  # inline-form
                                        # inline-form fields
                                        fields=['PersonID', 'FullName','BirthDay','Relation','Occupation','Salary','Education'], 
                                        # fields=['PersonID', 'FullName','BirthDay','Relation','Occupation','Salary','Education'], 

                                        # labels for the fields
                                        labels={
                                            'PersonID': _(u'PersonID'),
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
                                        extra = 3)
