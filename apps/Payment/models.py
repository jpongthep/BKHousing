from datetime import date, datetime
from django.db import models


from apps.Home.models import HomeOwner

def first_day_of_month():
    return datetime.today().replace(day=1)

class WaterPayment(models.Model):
    class Meta:
        verbose_name_plural = "WaterPayment : ค่าน้ำประปา"
    home_owner = models.ForeignKey(HomeOwner, on_delete=models.CASCADE, related_name='WaterPayment')
    date = models.DateField(verbose_name="เดือน-ปี", null = True, blank = True, default = first_day_of_month)
    date_meter = models.DateField(verbose_name="วันที่จดค่าน้ำ", null = True, blank = True, default = datetime.today)
    meter = models.IntegerField(verbose_name="เลขมิเตอร์น้ำ", null = True, blank = True, default = 0)
    units = models.IntegerField(verbose_name="หน่วยน้ำ", null = True, blank = True, default = 0)
    bill = models.IntegerField(verbose_name="ค่าน้ำ", null = True, blank = True, default = 0)
    comment = models.TextField(verbose_name="หมายเหตุค่าน้ำ",null = True, blank = True)
    
    def get_absolute_url(self):
        pass
        # return reverse('Home:owner_detail', kwargs={"pk": hmowner_id}) 

    def __str__(self):
        return self.home_owner.owner.FullName + ' : ' + str(self.date)

class RentPayment(models.Model):
    class Meta:
        verbose_name_plural = "RentPayment : ค่าบำรุงแรกเข้า / รายเดือน"
    home_owner = models.ForeignKey(HomeOwner, on_delete=models.CASCADE, related_name='RentPayment')
    PersonID = models.CharField(verbose_name="เลขบัตรประชาชน", max_length = 13, null=True, blank=True, default = '' )
    date = models.DateField(verbose_name="เดือน-ปี", null = True, blank = True, default = first_day_of_month)
    first_bill = models.IntegerField(verbose_name="ค่าบำรุงแรกเข้า", null = True, blank = True, default = 0)
    montly_bill = models.IntegerField(verbose_name="ค่าบำรุงรายเดือน", null = True, blank = True, default = 0)
    comment = models.TextField(verbose_name="หมายเหตุค่าบำรุง",null = True, blank = True)
    
    def get_absolute_url(self):
        pass
        # return reverse('Home:owner_detail', kwargs={"pk": hmowner_id}) 

    def __str__(self):
        return self.home_owner.owner.FullName + ' : ' + str(self.date)

