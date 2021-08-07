import json
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate as django_authenticate

import requests as rq

from .models import User, Unit


def checkRTAFPassdword(username, password):
    pass
    URL = "https://api2-software.rtaf.mi.th:5051/rtaf/v3/ad/internal/login"

    data = {
        'user' : username.lower(),
        'pass' : password
    } 

    r = rq.post(url = URL, data = data, verify=False) 

    return_STR_JSON = r.text 
    returnData = json.loads(return_STR_JSON)

    # print(type(pastebin_url))
    if returnData['result'] == "Process-Complete":
        return returnData
    else:
        return False


class SettingsBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None):
        pass
        # print('Username = ',username)
        try:
            user = User.objects.get(username=username)

            if not user.is_active:
                return None

            if username in ['test_user',]:
                return user

            # if not re.search("@rtaf.mi.th$",user.email):
            #     user = django_authenticate(username=username, password=password)
            #     if user is not None:
            #         return user
            #     else:
            #         messages.error(request,f'password สำหรับ  User "{username}" ไม่ถูกต้อง')
            #         return None

            pwd_valid = checkRTAFPassdword(username,password)

            if pwd_valid:
                return user
            else:
                messages.error(request,f'password สำหรับ  User  "{username}" ไม่ถูกต้อง')
                return None
                
        except User.DoesNotExist:
            ReturnData = checkRTAFPassdword(username,password)
            if ReturnData:
                user = User(username = username)
                user.email = f'{username}@rtaf.mi.th'                
                user.is_active = False
                user.is_staff = False
                user.is_superuser = False
                user.first_name = ReturnData['user_name']
                user.last_name = ""
                user.Unit = ReturnData['user_orgname']
                user.save()

                UserUnit = Unit.objects.filter(ShortName = ReturnData['user_orgname'])
                if not UserUnit.exists():                    
                    NewUnit = Unit(ShortName = ReturnData['user_orgname'], FullName = ReturnData['user_orgname'])
                    NewUnit.save()                

                messages.warning(request,f'ไม่มีผู้ใช้นี้ในระบบ ได้ทำการเพิ่ม "{username}" ให้แล้ว ติดต่อ Admin เพื่อเข้าใช้งาน')
            else:                
                messages.error(request,f'ไม่มีผู้ใช้ "{username}" ในระบบ')

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None