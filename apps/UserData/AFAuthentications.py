import json
import re
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth.models import Group
from django.conf import settings

import requests as rq

from .models import User, Unit
from apps.Home.models import HomeOwner
from apps.Utility.Constants import RTAFUnitSection


def checkRTAFPassdword(request, username, password):
    # URL = "https://api2-software.rtaf.mi.th:5051/rtaf/v3/ad/internal/login"
    URL = "https://otp.rtaf.mi.th/api/v2/mfa/login"

    data = {
        'user' : username.lower(),
        'pass' : password
    } 

    
    try:
        r = rq.post(url = URL, data = data, verify=False)
    except:
        messages.error(request, "ไม่สามารถติดต่อกับ LDAP Server ทอ.ได้ ")
        return False

    return_STR_JSON = r.text 
    returnData = json.loads(return_STR_JSON)

    # print(type(pastebin_url))
    if returnData['result'] == "Process-Complete":
        return returnData
    else:
        messages.error(request, "username หรือ รหัสผ่านไม่ถูกต้อง ")
        return False

def getUserByRTAFemail(email, token):
    URL = "https://otp.rtaf.mi.th/api/gateway/rtaf/hris_api_1/RTAFHousePerson"
    data = {
        "token" : token,
        "email" : email + '@rtaf.mi.th'
    } 
    r = rq.post(url = URL, data = data, verify=False) 

    return_data = json.loads(r.text)

    # ไม่พบข้อมูล
    if return_data['data'] == 'ไม่มีข้อมูล':
        return None
    return_data = return_data['data'][0]

    search_unit = Unit.objects.filter(ShortName = return_data['UNITNAME'])
    if search_unit.exists():
        user_unit = search_unit[0]
    else:
        user_unit = Unit(
                        UnitGroup = '0', 
                        ShortName =  return_data['UNITNAME'], 
                        FullName = return_data['UNITNAME']
                    )
        user_unit.save()
    
    try:
        search_user = User.objects.get(username = return_data['PEOPLEID'])
        search_user.username = email
        search_user.first_name = return_data['FIRSTNAME']
        search_user.last_name = return_data['LASTNAME']
        search_user.email = email+'@rtaf.mi.th'
        search_user.is_active = True
        search_user.PersonID = return_data['PEOPLEID']
        search_user.AFID = return_data['ID']
        search_user.BirthDay = datetime.strptime(return_data['BIRTHDATE'][:10], '%Y-%m-%d')
        search_user.retire_date = datetime.strptime(return_data['RETIREDATE'][:10], '%Y-%m-%d')
        search_user.Rank = int(return_data['RANKID'])
        search_user.Position = return_data['POSITION']
        search_user.CurrentUnit = user_unit
        search_user.current_salary = float(return_data['SALARY'],)
        search_user.current_status = return_data['MARRIED']
        search_user.current_spouse_name = return_data['SPOUSE_NAME']
        search_user.current_spouse_pid = return_data['SPOUSE_IDCARD']
        search_user.Address = return_data['ADDRESS']
        search_user.date_joined = datetime.today()
        search_user.save()
        user = search_user
    except User.DoesNotExist:        
        new_user = User(username = email,
                        first_name = return_data['FIRSTNAME'],
                        last_name = return_data['LASTNAME'],
                        email = email+'@rtaf.mi.th',
                        is_active = True,
                        PersonID = return_data['PEOPLEID'],
                        AFID = return_data['ID'],
                        BirthDay = datetime.strptime(return_data['BIRTHDATE'][:10], '%Y-%m-%d'),
                        retire_date = datetime.strptime(return_data['RETIREDATE'][:10], '%Y-%m-%d'),
                        Rank = int(return_data['RANKID']),
                        Position = return_data['POSITION'],
                        CurrentUnit = user_unit,
                        current_salary = float(return_data['SALARY'],),
                        current_status = return_data['MARRIED'],
                        current_spouse_name = return_data['SPOUSE_NAME'],
                        current_spouse_pid = return_data['SPOUSE_IDCARD'],
                        Address = return_data['ADDRESS']
                        )
        new_user.save()
        # print('User.DoesNotExist ')
        user = new_user

    #ค้นหาว่ามีบ้านที่พักอยู่หรือไม่
    home_owner = HomeOwner.objects.filter(owner = user).filter(is_stay = True)
    if home_owner.exists():
        home_status = Group.objects.get(name='RTAF_HOME_USER') 
    elif user.current_spouse_pid:
        # ถ้ามีคู่สมรสตรวจสอบว่าเป็นคู่สมรสเจ้าของบ้านหรือไม่
        try:
            spouse_user = User.objects.get(PersonID = user.current_spouse_pid)
            spouse_home = HomeOwner.objects.filter(owner = spouse_user).filter(is_stay = True)
            if spouse_home.exists():
                home_status = Group.objects.get(name='RTAF_HOME_SPOUSE')
            else:
                home_status = Group.objects.get(name='RTAF_NO_HOME_USER') 
        except:
            home_status = Group.objects.get(name='RTAF_NO_HOME_USER') 
    else:
        home_status = Group.objects.get(name='RTAF_NO_HOME_USER') 
        
    user.groups.add(home_status)

    return user

def getPersonID(person_data):

    URL = "https://otp.rtaf.mi.th/api/gateway/covid19/rtaf/personal/idcard/by/name"

    full_name = person_data['user_name']

    # แยกยศ ชื่อ นามสกุล
    rank = re.findall("[(ว่าที่)]*[ ]*[(พล.อ)]*[(พ.อ.)]*[นรจ]*\.[สตทอ]\.[(หญิง)]*", full_name)[0]
    first_name, last_name = full_name.replace(rank, "").strip().split()

    data = {
        "token" : person_data['token'],
        "fname" : first_name,
        "lname": last_name
    } 

    r = rq.post(url = URL, data = data, verify=False) 

    return_data = json.loads(r.text)
    # print('return_data = ',return_data)
    if 'data' not in return_data: 
        return None
    if  not return_data['data']: 
        return None
    
    return_data = return_data['data'][0]

    return return_data['national_id']


def UpdateRTAFData(current_user,person_data):
    URL = "https://otp.rtaf.mi.th/api/gateway/covid19/rtaf/personal/idcard/by/name"

    full_name = person_data['user_name']

    # แยกยศ ชื่อ นามสกุล
    rank = re.findall("[(ว่าที่)]*[ ]*[(พล.อ)]*[(พ.อ.)]*[นรจ]*\.[สตทอ]\.[(หญิง)]*", full_name)[0]
    first_name, last_name = full_name.replace(rank, "").strip().split()

    data = {
        "token" : person_data['token'],
        "fname" : first_name,
        "lname": last_name
    } 

    r = rq.post(url = URL, data = data, verify=False) 

    return_data = json.loads(r.text)
    # print('return_data = ',return_data)
    if 'data' not in return_data: 
        return
    if  not return_data['data']: 
        return
    

    return_data = return_data['data'][0]


    current_user.PersonID = return_data['national_id']
    current_user.BirthDay = return_data['birthday']

    UserUnit = Unit.objects.filter(ShortName = return_data['unitname'])
    if not UserUnit.exists():                    
        NewUnit = Unit(ShortName = return_data['unitname'], FullName = return_data['unitname'])
        NewUnit.save() 
        UserUnit = NewUnit
    else:
        UserUnit = UserUnit[0]

    current_user.CurrentUnit = UserUnit                
    current_user.save()


    URL = "https://otp.rtaf.mi.th/api/gateway/rtaf/hris_api_1/RTAFHousePerson"
    data = {
        "token" : person_data['token'],
        "national_id" : current_user.PersonID
    } 

    r = rq.post(url = URL, data = data, verify=False) 

    return_data = json.loads(r.text)
    if 'data' not in return_data: 
        return
    if  not return_data['data']: 
        return

    return_data = return_data['data'][0]
    
    # print('return_data = ',return_data)
    current_user.first_name = return_data['FIRSTNAME']
    current_user.last_name = return_data['LASTNAME']   
    current_user.AFID = return_data['ID']
    current_user.RTAFEMail = current_user.username + '@rtaf.mi.th'
    current_user.Rank = int(return_data['RANKID'])
    current_user.Position = return_data['POSITION']
    current_user.retire_date = datetime.strptime(return_data['RETIREDATE'][:10], '%Y-%m-%d')
    current_user.current_salary = float(return_data['SALARY'])
    current_user.Address = return_data['ADDRESS']
    current_user.save()

    # ตรวจสอบว่ามีคู่สมรสหรือไม่
    if not return_data['SPOUSE_IDCARD']:
        return 
    else:
        current_user.current_spouse_pid = return_data['SPOUSE_IDCARD']
        current_user.save()

        # ตรวจสอบว่าคู่สมรสเป็น ทอ. ?
        data = {
            "token" : person_data['token'],
            "national_id" : current_user.current_spouse_pid
        } 

        r = rq.post(url = URL, data = data, verify=False) 

        return_data = json.loads(r.text)
        if 'data' not in return_data: 
            return
        if  return_data['data'] == 'ไม่มีข้อมูล': 
            return      
        if  not return_data['data']: 
            return      

        return_data = return_data['data']
        # กรณีที่คู่สมรสเป็น ทอ.
        # print(return_data)
        current_user.current_spouse_name = return_data['RANK'] + return_data['FIRSTNAME'] + '  ' + return_data['LASTNAME']
        current_user.save()
    

class SettingsBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None):

        #กรณีใส่ @rtaf.mi.th มาด้วยก็เอาออกก่อน
        if re.search("@rtaf.mi.th$",username.lower()) : username =  username[0:-11]
        username = username.lower()
        try:
            user = User.objects.get(username=username)
            pwd_valid = checkRTAFPassdword(request, username,password)
            if pwd_valid:
                UpdateRTAFData(user,pwd_valid)
                print("login_mode = ",pwd_valid["login_mode"])
                if pwd_valid["login_mode"] == "AD-Login":                    
                    user.set_password(password)
                    user.save()
                # print('login user = ', user)
                return user
            else:                
                return None

        except User.DoesNotExist:
            # ตรวจสอบ username และ password
            ReturnData = checkRTAFPassdword(request, username,password)

            if not ReturnData:
                return None

            auth_user = getUserByRTAFemail(username, ReturnData['token'])
            auth_user.set_password(password)
            auth_user.save()
            return auth_user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None