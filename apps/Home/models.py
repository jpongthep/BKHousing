from django.db import models
from django.urls import reverse

from apps.Utility.UploadData import UploadFolderName
from apps.Utility.Constants import ( HomeDataType, 
                                     HomeZone, 
                                     HomeDataStatus, 
                                     HomeDataGrade,
                                     OwnerLeaveType)

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

    def get_absolute_url(self):
        return reverse('Home:detail', kwargs={"pk": hm_id})    

    def __str__(self):
        return f'{self.number} {self.get_type_display()} {self.get_zone_display()}'

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

    def get_absolute_url(self):
        return reverse('Home:owner_detail', kwargs={"pk": hmowner_id}) 

    def __str__(self):
        if self.is_stay:
            return 'พักอาศัย | ' + self.owner.FullName + ' : ' + self.home.__str__()
        else:
            return 'ย้ายออก | ' + self.owner.FullName + ' : ' + self.home.__str__()
