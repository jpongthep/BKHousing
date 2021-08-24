from django.db import models

from apps.Utility.UploadData import UploadFolderCommandFile


class Command(models.Model):
    class Meta:
        verbose_name_plural = "Command : คำสั่งบ้านพัก"        
        constraints = [
        models.UniqueConstraint(fields=['number', 'year'], name='command_number')
    ]
        
    number = models.PositiveIntegerField(verbose_name='เลขที่', null = False, blank = False, default = 1)
    year = models.PositiveIntegerField(verbose_name='ปี', null = False, blank = False, default = 64)
    name = models.CharField(verbose_name="ชื่อเรื่อง", max_length = 150, null = False, blank = False, default = '-')
    date_sign = models.DateField(verbose_name="วันลงนาม", null = True, blank = True)
    date_effect = models.DateField(verbose_name="วันมีผล", null = True, blank = True)
    date_due = models.DateField(verbose_name="วันหมดสิทธิ์", null = True, blank = True)
    file= models.FileField(verbose_name='ไฟล์คำสั่ง', default = None, null = True, blank = True, upload_to = UploadFolderCommandFile)

    def __str__(self):
        return f'{self.number}/{self.year}'
