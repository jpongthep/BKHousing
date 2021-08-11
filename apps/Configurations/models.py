import datetime

from django.db import models

# from apps.Trouble.models import SetForm
from apps.Utility.Constants import YEARROUND_PROCESSSTEP

class YearRound(models.Model):
    class Meta:
        verbose_name_plural = "Year-Round : ปี - วงรอบ" 
    Year  = models.IntegerField(default = datetime.date.today().year,verbose_name = 'ปีปัจจุบัน')
    Round = models.IntegerField(default = 1,verbose_name = 'วงรอบ')

    CurrentStep = models.IntegerField(choices=YEARROUND_PROCESSSTEP, default=0,verbose_name = 'การทำงานในขณะนี้')
    Step1 = models.DateField(verbose_name = 'ส่งคำร้อง')
    Step2 = models.DateField(verbose_name = 'นขต.ประเมิน')
    Step3 = models.DateField(verbose_name = 'กพ.ดำเนินการ')
    # TroubleForm = models.ForeignKey('SetForm', null=True,  blank=True, on_delete = models.SET_NULL, verbose_name = 'ฟอร์มประเมิน')
    def __str__(self):
        return f'{self.Year}-{self.Round}'