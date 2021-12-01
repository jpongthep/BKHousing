import requests as rq
import json
import re
from datetime import datetime
import logging

from django.contrib import messages
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth.models import Group
from django.conf import settings
from django.db.models import Q

from .models import User, Unit
from apps.Home.models import HomeOwner
from apps.Configurations.models import YearRound
from apps.Utility.Constants import YEARROUND_PROCESSSTEP

logger = logging.getLogger('LoginLog')


def checkRTAFPassdword(request, username, password):
    # URL = "https://api2-software.rtaf.mi.th:5051/rtaf/v3/ad/internal/login"
    URL = "https://otp.rtaf.mi.th/api/v2/mfa/login"

    data = {
        'user' : username.lower(),
        'pass' : password
    } 
    # data = {
    #     'user' : "pong",
    #     'pass' : ""
    # } 

    
    try:
        r = rq.post(url = URL, data = data, verify=False)
    except:
        messages.error(request, "login LDAP ขัดข้อง กรุณาทดสอบโดยเข้า email ของ ทอ. หากไม่ได้กรุณาตรวจสอบกับ link ทดสอบการ login หรือติดต่อ 2-8641")
        return False

    logger.info(f'{username} {r.text}')
    return_STR_JSON = r.text 
    returnData = json.loads(return_STR_JSON)

    # print(type(pastebin_url))
    if 'result' not in returnData:
        messages.error(request, "login LDAP ขัดข้อง กรุณาตรวจสอบกับ link ทดสอบการ login")
        return False

    if returnData['result'] == "Process-Complete":
        return returnData
    else:
        if len(returnData['error']) > 1:
            count_error_text = returnData['error'][0] + "  " + returnData['error'][1]
        else:
            count_error_text = "username หรือ รหัสผ่านไม่ถูกต้อง " 
        messages.error(request, count_error_text)
        return False

def getUserByRTAFemail(request, email, token):
    URL = "https://otp.rtaf.mi.th/api/gateway/rtaf/hris_api_1/RTAFHousePerson"
    data = {
        "token" : token,
        "email" : email + '@rtaf.mi.th'
    } 
    r = rq.post(url = URL, data = data, verify=False) 

    return_data = json.loads(r.text)

    # print(type(pastebin_url))
    if 'result' not in return_data:
        messages.error(request, "การติดต่อ HRIS ขัดข้อง")
        return False

    # ไม่พบข้อมูล
    if return_data['result'] != "Process-Complete":
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
        search_user.retire_date = datetime.strptime(return_data['RETIREDATE'][:10], '%Y-%m-%d') if return_data['RETIREDATE'] else None
        search_user.Rank = int(return_data['RANKID'])
        search_user.Position = return_data['POSITION']
        search_user.CurrentUnit = user_unit
        search_user.current_salary = float(return_data['SALARY'],)
        search_user.current_status = return_data['MARRIED'] if return_data['MARRIED'] else 1
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
                        retire_date = datetime.strptime(return_data['RETIREDATE'][:10], '%Y-%m-%d') if return_data['RETIREDATE'] else None,
                        Rank = int(return_data['RANKID']),
                        Position = return_data['POSITION'],
                        CurrentUnit = user_unit,
                        current_salary = float(return_data['SALARY'],),
                        current_status = return_data['MARRIED'] if return_data['MARRIED'] else 1,
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

def getPersonID(request, person_data):

    URL = "https://otp.rtaf.mi.th/api/gateway/covid19/rtaf/personal/idcard/by/name"

    full_name = person_data['user_name']

    # แยกยศ ชื่อ นามสกุล
    rank = re.findall("[(ว่าที่)]*[ ]*[(พล.อ)]*[(พ.อ.)]*[นรจ]*\.[สตทอ]\.[(หญิง)]*", full_name)[0]
    first_name = person_data['fname']
    last_name = person_data['lname']
    
    # fullname = full_name.replace(rank, "").strip().split()
    # if len(fullname) == 2:
    #     first_name = fullname[0]
    #     last_name = fullname[1]
    # else:
    #     first_name = fullname[0]
    #     last_name = " ".join(fullname[1:])

    # print("first_name = ", first_name)
    # print("last_name = ", last_name)

    data = {
        "token" : person_data['token'],
        "fname" : first_name,
        "lname": last_name
    } 

    r = rq.post(url = URL, data = data, verify=False) 

    return_data = json.loads(r.text)
    # print(type(pastebin_url))
    if 'result' not in return_data:
        messages.error(request, "การติดต่อ HRIS ขัดข้อง")
        return None

    # ไม่พบข้อมูล
    if return_data['result'] != "Process-Complete":
        return None

    if 'data' not in return_data: 
        return None
    if  not return_data['data']: 
        return None
    
    return_data = return_data['data'][0]

    return return_data['national_id']


def UpdateRTAFData(request, current_user,person_data):
    URL = "https://otp.rtaf.mi.th/api/gateway/covid19/rtaf/personal/idcard/by/name"

    full_name = person_data['user_name']

    # แยกยศ ชื่อ นามสกุล
    rank = re.findall("[(ว่าที่)]*[ ]*[(พล.อ)]*[(พ.อ.)]*[นรจ]*\.[สตทอ]\.[(หญิง)]*", full_name)[0]
    first_name = person_data['fname']
    last_name = person_data['lname']

    # else:
    # fullname = full_name.replace(rank, "").strip().split()
    
    # if len(fullname) == 2:
    #     first_name = fullname[0]
    #     last_name = fullname[1]
    # else:
    #     first_name = fullname[0]
    #     last_name = " ".join(fullname[1:])

    print("first_name = ",first_name)
    print("last_name = ",last_name)

    data = {
        "token" : person_data['token'],
        "fname" : first_name,
        "lname": last_name
    } 
    # data = {
    #     "token" : person_data['token'],
    #     "fname" : "กนกพร",
    #     "lname": "วันหนุน"
    # } 

    r = rq.post(url = URL, data = data, verify=False) 


    return_data = json.loads(r.text)
    # print('return_data = ',return_data)
    if 'result' not in return_data:
        messages.error(request, "การติดต่อ HRIS ขัดข้อง")
        return None

    # ไม่พบข้อมูล
    if return_data['result'] != "Process-Complete":
        return None

    if 'data' not in return_data: 
        return
    if  not return_data['data']: 
        return
    

    return_data = return_data['data'][0]


    current_user.PersonID = return_data['national_id']
    if return_data['birthday'] != "-":
        current_user.BirthDay = return_data['birthday']

    UserUnit = Unit.objects.filter(ShortName = return_data['unitname'])
    if not UserUnit.exists():                    
        NewUnit = Unit(ShortName = return_data['unitname'], FullName = return_data['unitname'])
        NewUnit.save() 
        UserUnit = NewUnit
    else:
        UserUnit = UserUnit[0]

    current_user.sub_unit = UserUnit.ShortName
    if UserUnit.sub_unit_list: # ถ้ามีการระบุหน่วยย่อยในหน่วยงาน
        sub_unit_list = str(UserUnit.sub_unit_list)
        sub_unit_list = [x.strip() for x in sub_unit_list.split(",")]

        if current_user.Position:
            match = next((x for x in sub_unit_list if x in current_user.Position), False)
            print("#",current_user.Position, match)
            if match:
                current_user.sub_unit = match

    current_user.CurrentUnit = UserUnit                
    current_user.save()


    URL = "https://otp.rtaf.mi.th/api/gateway/rtaf/hris_api_1/RTAFHousePerson"
    data = {
        "token" : person_data['token'],
        "national_id" : current_user.PersonID
    } 

    r = rq.post(url = URL, data = data, verify=False) 

    return_data = json.loads(r.text)
    
    if 'result' not in return_data:
        messages.error(request, "การติดต่อ HRIS ขัดข้อง")
        return None

    # ไม่พบข้อมูล
    if return_data['result'] != "Process-Complete":
        messages.error(request, "ไม่พบข้อมูลจาก HRIS")
        return None

    if 'data' not in return_data: 
        return
    if  not return_data['data']: 
        return

    # print('return_data = ',return_data)
    return_data = return_data['data'][0]
    # print('return_data = ',return_data)
    current_user.first_name = return_data['FIRSTNAME']
    current_user.last_name = return_data['LASTNAME']   
    current_user.AFID = return_data['ID']
    current_user.RTAFEMail = current_user.username + '@rtaf.mi.th'
    current_user.Rank = int(return_data['RANKID'])
    current_user.Position = return_data['POSITION']
    current_user.retire_date = datetime.strptime(return_data['RETIREDATE'][:10], '%Y-%m-%d') if return_data['RETIREDATE'] else None
    current_user.current_salary = float(return_data['SALARY'])
    current_user.Address = return_data['ADDRESS']
    # print("return_data['MARRIED'] ", return_data['MARRIED'])
    # print("type(return_data['MARRIED)'] ", type(int(return_data['MARRIED'])))
    current_user.current_status = int(return_data['MARRIED']) if return_data['MARRIED'] else 1
    current_user.save()

    # ตรวจสอบว่ามีคู่สมรสหรือไม่
    if not return_data['SPOUSE_IDCARD']:
        return 
    elif return_data['MARRIED'] == "2":
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

        return_data = return_data['data'][0]
        # กรณีที่คู่สมรสเป็น ทอ.
        # print(return_data)
        # print(return_data['RANK'])
        # print(return_data['FIRSTNAME'])
        # print(return_data['LASTNAME'])
        # print(return_data['RANK'] + return_data['FIRSTNAME'] + '  ' + return_data['LASTNAME'])
        current_user.current_spouse_name = return_data['RANK'] + return_data['FIRSTNAME'] + '  ' + return_data['LASTNAME']
        current_user.save()
    

class SettingsBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None):

        ActiveYearRound = YearRound.objects.filter(CurrentStep__in = ['RS', 'UP', 'PP'])
        UseHRIS = ActiveYearRound[0].load_HRIS
        # กรณีใส่ @rtaf.mi.th มาด้วยก็เอาออกก่อน
        # if re.search("@rtaf.mi.th$",username.lower()) : username =  username[0:-11]
        username = username.lower()

        special_characters = "!#$%^&*()-+?=,<>/\\\"\'"        

        # ถ้ามีการกรอกตัวอักษรพิเศษเข้ามากับ username ก็ reject ได้เลย
        if any(c in special_characters for c in username):
            # print("special character")
            logger.info(f'{username} reject by special characters')
            return None
        
        try:
            user = User.objects.get(username=username)
            pwd_valid = checkRTAFPassdword(request, username,password)
            if pwd_valid:
                if UseHRIS : UpdateRTAFData(request, user,pwd_valid)
                # print("login_mode = ",pwd_valid["login_mode"])
                if pwd_valid["login_mode"] == "AD-Login":                    
                    user.set_password(password)
                    user.save()
                # print('login user = ', user)
                request.session['Token'] = pwd_valid['token']
                request.session['password'] = password
                logger.info(f'{username} login success')
                return user
            else:                
                logger.warning(f'{username} login OTP fail')
                return None

        except User.DoesNotExist:
            # ตรวจสอบ username และ password
            ReturnData = checkRTAFPassdword(request, username,password)

            if not ReturnData:
                logger.info(f'{username} new user otp fail to login')
                return None

            if not UseHRIS : 
                messages.error(request, "ติดต่อ HRIS ขัดข้อง (admin : 2-8641)")
                logger.info(f'{username} first login but disable HRIS')
                return None
            else:
                auth_user = getUserByRTAFemail(request, username, ReturnData['token'])
                auth_user.set_password(password)
                auth_user.save()
                logger.info(f'{username} first login success')
                return auth_user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None