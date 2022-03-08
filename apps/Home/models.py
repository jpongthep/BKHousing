from datetime import date

from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.urls import reverse

from apps.Utility.UploadData import UploadFolderName
from apps.Utility.Constants import ( HomeDataType, 
                                     HomeZone, 
                                     HomeDataStatus, 
                                     HomeDataGrade,
                                     OwnerLeaveType,
                                     CoResidenceRelation,
                                     EDUCATION)

from apps.UserData.models import User, Unit
from apps.Command.models import Command

class HomeData(models.Model):
    class Meta:
        verbose_name_plural = "HomeData : ข้อมูลบ้านพัก"

    finance_id = models.PositiveIntegerField(verbose_name='รหัสการเงิน')
    type = models.CharField(verbose_name="ประเภท", max_length = 4, choices = HomeDataType.choices, default = HomeDataType.RF)
    zone = models.CharField(verbose_name="เขต", max_length = 2, choices = HomeZone.choices, default = HomeZone.Z1)
    location_name = models.CharField(verbose_name="ชื่อพิกัด", max_length = 30, null = True, blank = True)
    building_number = models.CharField(verbose_name="อาคาร", max_length = 10, null = True, blank = True)
    room_number = models.CharField(verbose_name="ห้อง", max_length = 5, null = True, blank = True)
    number = models.CharField(verbose_name="บ้านเลขที่", max_length = 10, null = True, blank = True)
    status = models.CharField(verbose_name="สถานะ", max_length = 2, choices = HomeDataStatus.choices, default = HomeDataStatus.STAY)
    status_fix_year =  models.IntegerField(verbose_name='สถานะซ่อม ปี', null = True, blank = True)
    grade = models.CharField(verbose_name="เกรด", max_length = 2, choices = HomeDataGrade.choices, default = HomeDataGrade.NO)
    monthly_fee = models.IntegerField(verbose_name='ค่าบำรุงรายเดือน', null = True, blank = True)
    enter_fee = models.IntegerField(verbose_name='ค่าบำรุงแรกเข้า', null = True, blank = True)
    comment = models.TextField(verbose_name='หมายเหตุ', null = True, blank = True)
    owner = models.ManyToManyField(User, through='HomeOwner')

    # def get_absolute_url(self):
    #     return reverse('Home:detail', kwargs={"pk": hm_id})    

    def __str__(self):
        building_number = f"อ.{self.building_number}" if self.building_number != "-" else ""
        room_number = f"{self.room_number}" if self.room_number != "-" else ""        
        ZoneName = {
                        '1' : 'เขต 1', 
                        '2' : 'เขต 2', 
                        '3' : 'เขต 3',
                        '6T' : 'เขต 6 รถไฟ', 
                        '6S' : 'เขต 6 สีกัน', 
                        '7S' : 'เขต 7 ลาดเป็ด', 
                        'BS' : 'บางซื่อ'}
        if self.zone in ZoneName:
            ZoneName = ZoneName[self.zone]
        else:
            ZoneName = f"--{self.zone}--"

        if "ฟ" in self.get_type_display():
            return f"{self.get_type_display()} {self.building_number} ห้อง {self.room_number} {ZoneName} บ้านเลขที่ {self.number}"
        elif "ร" in self.get_type_display():
            return f"{self.get_type_display()}{self.building_number} ห้อง {self.room_number} {ZoneName} บ้านเลขที่ {self.number}"
        elif "ป" in self.get_type_display():
            return f"{self.get_type_display()} {self.building_number} ห้อง {self.room_number} {ZoneName} บ้านเลขที่ {self.number}"
        elif self.type == "HO5":
            return f"{self.get_type_display()} {self.building_number}{self.room_number} {ZoneName}"
        else:
            return f"{self.get_type_display()}{self.building_number} {ZoneName} บ้านเลขที่ {self.number}"
    

# ชื่อบ้าน 
# พ.
# น.3077 เขต 3  บ้านเลขที่ 171/2507
# ร.1258 ห้อง 2 เขต 1 บ้านเลขที่ 171/3095 

# ร.
# ฟส.(โสด)
# ฟส.
# ฟป.8 ห้อง 523 เขต 6 สีกัน  บ้านเลขที่ 533/1793 
# ฟป.(โสด) 8 ห้อง 206 เขต 3  บ้านเลขที่ 171/2818

# ป.1            
        

class HomeOwner(models.Model):
    class Meta:
        verbose_name_plural = "HomeOwner : บ้านและผู้เข้าพัก"    
    owner = models.ForeignKey(User,verbose_name="เจ้าบ้าน", on_delete=models.CASCADE, related_name= "owner")
    home = models.ForeignKey(HomeData,verbose_name="บ้านพัก", on_delete=models.CASCADE, related_name= "home")
    is_stay = models.BooleanField(verbose_name='พักอาศัย', default = True)
    enter_command = models.ForeignKey(Command,verbose_name='คำสั่งเข้าพัก', on_delete=models.SET_NULL, related_name= "enter_command", null = True, blank = True)
    date_enter = models.DateField(verbose_name="เข้าพักเมื่อ", null = True, blank = True)
    leave_command = models.ForeignKey(Command, verbose_name='คำสั่งย้ายออก', on_delete=models.SET_NULL, related_name= "leave_command", null = True, blank = True)
    date_leave = models.DateField(verbose_name="ย้ายออกเมื่อ", null = True, blank = True)
    leave_type = models.CharField(verbose_name="ย้ายออกเพราะ", max_length = 2, choices = OwnerLeaveType.choices, default = OwnerLeaveType.STAY)
    leave_comment = models.TextField(verbose_name="หมายเหตุการย้ายออก",null = True, blank = True)
    insurance_rate = models.IntegerField(verbose_name="ค่าประกันบ้านพัก", null = True, blank = True, default = 2000)
    rent_rate = models.IntegerField(verbose_name="ค่าบำรุงรายเดือน", null = True, blank = True, default = 400)
    water_meter_insurance = models.IntegerField(verbose_name="ค่าประกันมิเตอร์น้ำ", null = True, blank = True, default = 800)
    water_meter = models.IntegerField(verbose_name="เลขมิเตอร์น้ำแรกเข้า", null = True, blank = True, default = 0)
    electric_meter = models.IntegerField(verbose_name="เลขมิเตอร์ไฟแรกเข้า", null = True, blank = True, default = 0)

    # def get_absolute_url(self):
    #     return reverse('HomeData:owner_detail', kwargs={"pk": id}) 

    def __str__(self):
        if self.is_stay:
            return 'พักอาศัย | ' + self.owner.FullName + ' : ' + self.home.__str__()
        else:
            return 'ย้ายออก | ' + self.owner.FullName + ' : ' + self.home.__str__()


# ผู้ที่พักอาศัยอยู่ร่วมกัน
class CoResident(models.Model):
    class Meta:
        constraints = [
                UniqueConstraint(fields=['home_owner_id', 'person_id'], name='home_owner_id_person_id')
            ]
    home_owner = models.ForeignKey(HomeOwner, on_delete=models.CASCADE, related_name='CoResident')
    person_id = models.CharField(verbose_name="เลขประจำตัวประชาชน", max_length = 13)
    full_name = models.CharField(verbose_name="ยศ - ชื่อ - นามสกุล", max_length = 150, null = False, blank = False, default = '')
    birth_day = models.DateField(verbose_name="วันเกิด", null = True, blank = True)
    relation = models.CharField(verbose_name="ความสัมพันธ์", max_length = 4, choices = CoResidenceRelation.choices)
    occupation = models.CharField(verbose_name="อาชีพ", max_length = 20, null = True, blank = True)
    salary = models.IntegerField(verbose_name="รายได้", null = True, blank = True, default = 0)
    is_airforce = models.BooleanField(verbose_name = "เป็น ขรก.ทอ.", default = False)
    education = models.IntegerField(verbose_name="การศึกษา", choices=EDUCATION.choices, null = True, blank = True)

    def age(self):
        today = date.today()
        if  today.year - self.birth_day.year == 0:
            return 1
        else:
            return today.year - self.birth_day.year

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        hm_ownid = self.home_owner.id
        return reverse('Home:detail', kwargs={"pk": hm_ownid})

# ข้อมูลสัตว์เลี้ยง
class PetData(models.Model):    
    home_owner = models.ForeignKey(HomeOwner, on_delete=models.CASCADE, related_name='pet', default = None)
    type = models.CharField(verbose_name="ชนิดสัตว์เลี้ยง", max_length = 5, default = "dog", choices = (('dog','หมา'),('cat','แมว')))
    name = models.CharField(verbose_name="ชื่อ", max_length = 50, null = False, blank = False,)
    birth_year = models.IntegerField(verbose_name="ปีเกิด", null = True, blank = True)
    sex = models.CharField(verbose_name="เพศ", max_length = 5, default = "male", choices = (('male','ตัวผู้'),('fem','ตัวเมีย')))
    appearances = models.TextField(verbose_name="สี-รูปร่าง-ลักษณะ", null = True)

    def __str__(self):
        return f"{self.type} : {self.name}"

    # def get_absolute_url(self):
    #     hm_ownid = self.home_owner.id
    #     return reverse('Home:detail', kwargs={"pk": hm_ownid})

# ข้อมูลยานพาหนะ รถยนต์ รถจักรยานยนต์ 
class VehicalData(models.Model):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['plate', 'province'], name='plate_province')
        ]
        
    home_parker = models.ForeignKey(HomeOwner, on_delete=models.CASCADE, related_name='HomeParker', null = True)
    plate = models.CharField(verbose_name="เลขทะเบียนรถ", max_length = 10, null = True)
    province = models.CharField(verbose_name="จังหวัด", max_length = 10, null = True)
    type = models.IntegerField(verbose_name="ประเภท", choices = ((1,"จักรยานยนต์"),(2,"เก๋ง"),(3,"SUV"),(4,"กะบะ"),(5,"อื่น ๆ")),null = True)
    brand = models.CharField(verbose_name="ยี่ห้อ", max_length = 15, null = True)
    color = models.CharField(verbose_name="สี", max_length = 10, null = True)
    registration = models.FileField(verbose_name="สำเนาทะเบียนรถ", null = True, blank = True)

    def __str__(self):
        return f"{self.brand} : {self.plate} {self.color}"


class HomeOwnerSummary(HomeOwner):
    class Meta:
        proxy = True
        verbose_name = 'Home Owner Summary'
        verbose_name_plural = 'Homes Owner Summary'