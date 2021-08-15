import re

from django.db import models
from django.contrib.auth.models import AbstractUser

from apps.Utility.Constants import (USER_PERMISSION, CHOICE_Rank )
# Create your models here.

class Unit(models.Model):

    class Meta:
        verbose_name_plural = "Unit : หน่วยขึ้นตรง ทอ." 
    ShortName = models.CharField(max_length = 20, blank = False)
    FullName = models.CharField(max_length = 90, blank = False)
    
    def __str__(self):
        return f'{self.ShortName}'


class User(AbstractUser):
    class Meta:        
        verbose_name_plural = "User : ผู้ใช้งานระบบ"         
        permissions = USER_PERMISSION

    AFID = models.CharField(verbose_name = "เลขประจำตัว ทอ.", max_length = 15, null = True)
    PersonID = models.CharField(verbose_name="เลขบัตรประชาชน", max_length = 13, null=False, blank=False, default = '' )
    BirthDay = models.DateField(verbose_name="วันเกิด", null = True, blank = True)    
    Rank = models.PositiveIntegerField(verbose_name="ยศ", choices = CHOICE_Rank, default = 0, null=True)
    Position  =  models.CharField(verbose_name="ตำแหน่ง", max_length=250, null = True, blank = True)

    OfficePhone = models.CharField(verbose_name="เบอร์ที่ทำงาน", max_length = 20, null=True)
    MobilePhone = models.CharField(verbose_name="มือถือ", max_length = 30, null=True)
    RTAFEMail = models.EmailField(verbose_name = "email ทอ.", null=True)

    CurrentUnit =  models.ForeignKey(Unit, verbose_name="สังกัด", on_delete=models.SET_NULL, null = True, related_name='CurrentUnit')
 
     # การบรรจุครั้งแรก อาจนำไปใส่ไว่้ใน User เนื่องจากข้อมูลชุดนี้ไม่เปลี่ยนแปลงตลอดอายุราชการ
    PlacementUnit = models.ForeignKey(Unit, verbose_name="สังกัดบรรจุ", on_delete=models.SET_NULL, null = True, related_name='PlacementUnit')
    command_of_placement = models.CharField(verbose_name="ที่คำสั่งบรรจุ", max_length = 100, null = True, blank = True)
    PlacementCommandDate = models.DateField(verbose_name="ลงวันที่", null = True, blank = True)
    PlacementDate = models.DateField(verbose_name="เริ่มบรรจุเมื่อ", null = True, blank = True)

    @property
    def Sex(self):
        RankDisplay = self.get_Rank_display()

        if RankDisplay in ['นาง', 'นางสาว','ญ.']:
            return 'หญิง'

        if re.findall("หญิง", RankDisplay ):
            return 'หญิง'
        else:
            return 'ชาย'
        
    @property
    def FullName(self):        
        RankDisplay = self.get_Rank_display()
        if RankDisplay == '':
            return  '??'

        if re.findall("หญิง", RankDisplay ):
            return f'{RankDisplay} {self.first_name} {self.last_name}'
        else:
            if re.findall("(พ)", RankDisplay ):
                return f'{RankDisplay} {self.first_name} {self.last_name}'
            else:
                return f'{RankDisplay}{self.first_name} {self.last_name}'
        
    def __str__(self):
        return self.FullName