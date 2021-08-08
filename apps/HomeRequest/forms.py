from django import forms

from .models import HomeRequest

class HomeRequestForm(forms.ModelForm):
    class Meta:
        model = HomeRequest
        fileds = '__all__'
        exclude = ['Requester', 'DateSend', 'YearRound', 'UnitApprover', 
                   'PersonApprover', 'IsTroubleSelf', 'IsTroubleUnit', 'IsTroublePerson']
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