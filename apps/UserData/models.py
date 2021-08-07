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

    Rank = models.PositiveIntegerField(choices = CHOICE_Rank, default = 0, null=True)
    Position  =  models.CharField(max_length=250, null = True, blank = True)
    OfficePhone =  models.CharField(max_length=10, null = True, blank = True)
    MobileTel =  models.CharField(max_length=20, null = True, blank = True)
    Unit =  models.ForeignKey(Unit, models.SET_NULL, null = True, verbose_name="สังกัด")
 
    @property
    def FullName(self):
        RankDisplay = self.get_Rank_display()
        if re.findall("หญิง", RankDisplay ):
            return f'{RankDisplay} {self.first_name} {self.last_name}'
        else:
            return f'{RankDisplay}{self.first_name} {self.last_name}'
        
    def __str__(self):
        return self.FullName



