from datetime import datetime, date, timedelta
import requests as rq
import json

from django.contrib.auth.models import Group
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import UpdateView, TemplateView
from django.urls import reverse
from django.contrib import messages

from .models import User, Unit
from apps.Home.models import HomeOwner
from apps.Payment.models import FinanceData
from .forms import MyAuthForm, UserCurrentDataForm, UnitUpdateForm
from apps.UserData.AFAuthentications import checkRTAFPassdword

from apps.Utility.Constants import FINANCE_CODE

class MyLoginView(LoginView):    
    authentication_form = MyAuthForm
    template_name = 'registration/new_login.html'


class UnitUpdateView(UpdateView):
    model = Unit
    form_class = UnitUpdateForm

class UserProfilesView(UpdateView):
    model = User
    form_class = UserCurrentDataForm
    template_name = "UserData/profile.html"

    def get_success_url(self):
        return reverse('UserData:profile', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        homerent_data = FinanceData.objects.filter(PersonID =  self.request.user.PersonID
                                          ).filter(date__gte = date.today() - timedelta(days = 185)
                                          ).filter(code = FINANCE_CODE.HOMERENT
                                          ).filter(money__gt = 0
                                          ).order_by("money","-date")
        if homerent_data.exists():
            data['rent'] = homerent_data[0].money
            data['rent_month'] = homerent_data[0].date
        else:
            data['rent'] = 0
        return data    

    def post(self, request, *args, **kwargs):
        messages.success(request,'บันทึกการแก้ไขเรียบร้อย')
        return super().post(request, *args, **kwargs)

def AddUserByPersonID(request, person_id):

    def TokenExpire(request,result):
        if "error" in result:
            if "name" in result["error"]:
                if result["error"]["name"] == "TokenExpiredError":
                    pwd_valid = checkRTAFPassdword(request, request.user.username,request.session['password'])
                    request.session['Token'] = pwd_valid['token']
                    return True
        return False

    check_exist = User.objects.filter(PersonID = person_id)
    if check_exist.exists():
        print("already exists")
        return "already exists"


    URL = "https://otp.rtaf.mi.th/api/gateway/rtaf/hris_api_1/RTAFHousePerson"

    token_expired = True
    while token_expired:
        try:
            data = {
                "token" : request.session['Token'],
                "national_id": person_id
            } 
            # print(f"API Search for pid = {person_id}")
            r = rq.post(url = URL, data = data, verify=False)
        except Exception as e:
            print("Request Error, ",e)
            return None

        return_data = json.loads(r.text)
        # print('return_data = ',return_data)
        token_expired = TokenExpire(request, return_data)

    if return_data['result'] == "Process-Error":
        return "Process-Error"

    if return_data['data'] == "ไม่มีข้อมูล":
        return "no data"

    ## ขั้นตอนการเพิ่ม  User
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
        search_user.username = person_id
        search_user.first_name = return_data['FIRSTNAME']
        search_user.last_name = return_data['LASTNAME']
        search_user.email = person_id
        search_user.is_active = False
        search_user.PersonID = return_data['PEOPLEID']
        search_user.AFID = return_data['ID']
        search_user.BirthDay = datetime.strptime(return_data['BIRTHDATE'][:10], '%Y-%m-%d') if return_data['BIRTHDATE'] else None
        search_user.retire_date = datetime.strptime(return_data['RETIREDATE'][:10], '%Y-%m-%d') if return_data['RETIREDATE'] else None
        search_user.Rank = int(return_data['RANKID'])
        search_user.Position = return_data['POSITION']
        search_user.CurrentUnit = user_unit
        search_user.current_salary = float(return_data['SALARY'],) if return_data['SALARY'] else None
        search_user.current_status = return_data['MARRIED'] if return_data['MARRIED'] else 1
        search_user.current_spouse_name = return_data['SPOUSE_NAME']
        search_user.current_spouse_pid = return_data['SPOUSE_IDCARD']
        search_user.Address = return_data['ADDRESS']
        # search_user.date_joined = datetime.today()
        search_user.save()
        user = search_user
    except User.DoesNotExist:        
        new_user = User(username = person_id,
                        first_name = return_data['FIRSTNAME'],
                        last_name = return_data['LASTNAME'],
                        email = person_id,
                        is_active = False,
                        PersonID = return_data['PEOPLEID'],
                        AFID = return_data['ID'],
                        BirthDay = datetime.strptime(return_data['BIRTHDATE'][:10], '%Y-%m-%d') if return_data['BIRTHDATE'] else None,
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

    return "create new"

    

