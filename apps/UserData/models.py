import re
import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

from apps.Utility.Constants import (USER_PERMISSION, 
                                    CHOICE_Rank, 
                                    RTAFUnitSection,
                                    PERSON_STATUS )
# Create your models here.

class Unit(models.Model):

    class Meta:
        verbose_name_plural = "Unit : หน่วยขึ้นตรง ทอ." 

    UnitGroup = models.CharField(max_length = 1, default = None, choices = RTAFUnitSection.choices)        
    ShortName = models.CharField(max_length = 20, blank = False)
    FullName  = models.CharField(max_length = 90, blank = False)
    is_Bangkok = models.BooleanField(verbose_name = "กทม.และปริมณฑล", default = True)
    sub_unit_list  = models.TextField(verbose_name = "รายชื่อหน่วยย่อย", null = True, blank = True)
    re_cal_sub_unit = models.BooleanField(verbose_name = "คำนวณหน่วยย่อย", default = True)
    line_notify_token = models.CharField(verbose_name = "line notify token", max_length = 43, null = True, blank = False)

    def __str__(self):
        return f'{self.ShortName}'


class User(AbstractUser):
    class Meta:        
        verbose_name_plural = "User : ผู้ใช้งานระบบ"         
        permissions = USER_PERMISSION

    AFID = models.CharField(verbose_name = "เลขประจำตัว ทอ.", max_length = 15, null = True)
    PersonID = models.CharField(verbose_name="เลขบัตรประชาชน", max_length = 13, null=True, blank=True, default = '' )
    BirthDay = models.DateField(verbose_name="วันเกิด", null = True, blank = True)    
    Rank = models.PositiveIntegerField(verbose_name="ยศ", choices = CHOICE_Rank, default = 0, null=True, blank=True)
    Position  =  models.CharField(verbose_name="ตำแหน่ง (ย่อ)", max_length=250, null = True, blank = True)

    OfficePhone = models.CharField(verbose_name="เบอร์ที่ทำงาน", max_length = 20, null=True, blank=True)
    MobilePhone = models.CharField(verbose_name="มือถือ", max_length = 30, null=True, blank=True)
    RTAFEMail = models.EmailField(verbose_name = "ที่อยู่ email ทอ.", null=True, blank=True)
    line_user_id = models.CharField(max_length = 40, unique = True, null=True, blank=True)

    sub_unit =  models.CharField(max_length = 30, verbose_name="สังกัดย่อย", null = True, blank=True)
    CurrentUnit =  models.ForeignKey(Unit, verbose_name="สังกัด", on_delete=models.SET_NULL, null = True, blank=True, related_name='CurrentUnit')
    current_salary = models.DecimalField(verbose_name="เงินเดือนปัจจุบัน", max_digits = 9, decimal_places = 2, null=True, blank=True)
    current_status = models.IntegerField(verbose_name="สถานภาพ", default = PERSON_STATUS.SINGLE, choices=PERSON_STATUS.choices, null=True, blank=True)
    current_spouse_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="ชื่อคู่สมรส")
    current_spouse_pid = models.CharField(max_length=13, null=True, blank=True, verbose_name="PID คู่สมรส")

    # ที่อยู่ปัจจุบัน
    Address = models.CharField(max_length = 100, null=True, blank=True, verbose_name="ที่อยู่")
    Province = models.CharField(max_length = 50, null=True, blank=True, verbose_name="จังหวัด")
     
     # การบรรจุครั้งแรก อาจนำไปใส่ไว่้ใน User เนื่องจากข้อมูลชุดนี้ไม่เปลี่ยนแปลงตลอดอายุราชการ
    PlacementUnit = models.ForeignKey(Unit, verbose_name="สังกัดบรรจุ", on_delete=models.SET_NULL, null = True, blank=True, related_name='PlacementUnit')
    command_of_placement = models.CharField(verbose_name="ที่คำสั่งบรรจุ", max_length = 100, null = True, blank = True)
    PlacementCommandDate = models.DateField(verbose_name="ลงวันที่", null = True, blank = True)
    PlacementDate = models.DateField(verbose_name="เริ่มบรรจุเมื่อ", null = True, blank = True)

    retire_date = models.DateField(verbose_name="วันทีเกษียณ", null = True, blank = True)
    hris_update = models.DateField(verbose_name="update กับ HRIS", null = False, default=datetime.date(2021,5,1))

    @property
    def Sex(self):
        RankDisplay = self.get_Rank_display()

        if RankDisplay in ['นาง', 'น.ส.']:
            return 'หญิง'
            
        if "ญ." in RankDisplay:
            return 'หญิง'

        if re.findall("หญิง", RankDisplay):
            return 'หญิง'
        else:
            return 'ชาย'

    @property
    def FullName(self):        
        RankDisplay = str(self.get_Rank_display())
        if RankDisplay == '':
            return  '??'
            
        if "ว่าที่" in RankDisplay:
            RankDisplay = RankDisplay[6:]
        elif "กห." in RankDisplay:
            if "หญิง" in RankDisplay:
                RankDisplay = "น.ส."
            else:
                RankDisplay = "นาย"
        elif "พนง." in RankDisplay:
            if "หญิง" in RankDisplay:
                RankDisplay = "น.ส."
            else:
                RankDisplay = "นาย"

        if re.findall("หญิง", RankDisplay ):
            return f'{RankDisplay} {self.first_name} {self.last_name}'
        elif re.findall("(พ)", RankDisplay ):
            RankDisplay = RankDisplay.replace("(พ)", "")    
        
        return f'{RankDisplay}{self.first_name} {self.last_name}'
        
    def __str__(self):
        return self.FullName


import string
import random

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))



