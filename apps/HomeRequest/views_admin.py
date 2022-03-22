from email import message
import logging
from datetime import date, timedelta

from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib import messages

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.Home.models import HomeOwner

#My module
from .models import HomeRequest, CoResident
from .serializers import ManualHomeRequestSerializer
from .views import AuthenUserTestMixin, get_current_year
from .forms import ManualHomeRequestForm, CrispyManualHomeRequestForm
from apps.UserData.models import User
from apps.UserData.forms import UserCurrentDataForm
from apps.UserData.views import AddUserByPersonID
from apps.Payment.models import FinanceData
from apps.Configurations.models import YearRound
from apps.Utility.Constants import FINANCE_CODE, HomeRentPermission, HomeRequestType, HomeRequestProcessStep

logger = logging.getLogger('Admin')


class ManualUpdateHomeRequestView(AuthenUserTestMixin, UpdateView):
    allow_groups = ['PERSON_ADMIN']
    model = HomeRequest
    # form_class = ManualHomeRequestForm
    form_class = ManualHomeRequestForm
    template_name = "Person/CreateManualHomeRequest.html"

    def get(self, request, *args, **kwargs):
            home_request = HomeRequest.objects.get(id = self.kwargs['pk'])
            
            user = home_request.Requester

            user_form = UserCurrentDataForm(instance = user, prefix = 'user')
            CurrentYearRound = YearRound.objects.filter(CurrentStep__in = ['RS','UP','PP'])
            # ถ้ามีคำขอบ้านอยู่แล้ว ก็แก้ใบเดิม

            form = ManualHomeRequestForm(instance = home_request)
            context = {'form': form, 'user_form' : user_form}
            return render(request, self.template_name, context)

    def form_valid(self, form):            
        hr = form.save(commit=False)
        hr.recorder = self.request.user
        hr.ProcessStep = HomeRequestProcessStep.PERSON_PROCESS
        hr.PersonDateRecieved = date.today()
        if not hr.Comment : 
            hr.Comment = "กรอกโดยตรงจาก จนท.กพ.ทอ."
        hr.save()
        messages.success(self.request,f"บันทึกข้อมูล {hr.Requester.FullName} เรียบร้อย")
        return super().form_valid(form)
    def get_success_url(self):        
        return reverse('HomeRequest:unitlist')


class ManualCreateHomeRequestView(AuthenUserTestMixin, CreateView):
    allow_groups = ['PERSON_ADMIN']
    model = HomeRequest
    # form_class = ManualHomeRequestForm
    form_class = ManualHomeRequestForm
    template_name = "Person/CreateManualHomeRequest.html"

    def get(self, request, *args, **kwargs):
            try:
                user = User.objects.get(PersonID = self.kwargs['person_id'])
                user.groups.add(Group.objects.get(name='RTAF_NO_HOME_USER'))                
            except:
                return render(request, "Person/person_id_not_found.html", {"person_id" : self.kwargs['person_id']})

            user_form = UserCurrentDataForm(instance = user, prefix = 'user')
            CurrentYearRound = YearRound.objects.filter(CurrentStep__in = ['RS','UP','PP'])
            home_request = HomeRequest.objects.filter(Requester = user).filter(year_round = CurrentYearRound[0])
                           
            #ถ้ายังไม่มีคำขอบ้าน ก็ตรวจสอบข้อมูล
            home_owner = HomeOwner.objects.filter(owner = user)
            if not home_owner.exists():
                Address = user.Address  
                request_type = HomeRequestType.NEW
            else:
                Address = f"{home_owner[0].home}  {home_owner[0].home.building_number}-{home_owner[0].home.room_number}"
                request_type = HomeRequestType.CHANGE

            initial_value = {
                    'Requester' : user,
                    'year_round' : CurrentYearRound[0],
                    'Rank': user.Rank,
                    'FullName': user.FullName,
                    'Position': user.Position,
                    'Unit': user.CurrentUnit,
                    # 'MobilePhone' : user.MobilePhone,
                    # 'OfficePhone' : user.OfficePhone,
                    # 'Unit' : user.CurrentUnit,
                    'Salary' : user.current_salary,
                    'Status' : user.current_status,
                    'SpouseName' : user.current_spouse_name,
                    'SpousePID' : user.current_spouse_pid,
                    'IsHRISReport' : user.current_status != 1,
                    'Address' : Address,
                    'request_type' : request_type,
                    'ProcessStep' : HomeRequestProcessStep.PERSON_PROCESS,
                    'PersonDateRecieved': date.today()
                }    
            # เช็คข้อมูลการเบิก คชบ.ของตนเอง ในช่วง 6 เดือนล่าสุด
            homerent_data = FinanceData.objects.filter(PersonID = user.PersonID
                                            ).filter(date__gte = date.today() - timedelta(days = 185)
                                            ).filter(code = FINANCE_CODE.HOMERENT
                                            ).filter(money__gt = 0
                                            ).order_by("money")
                
            initial_value['have_rent'] = False
            # print('homerent_data',homerent_data)
            if(homerent_data.exists()):
                initial_value['RentPermission'] = HomeRentPermission.used
                initial_value['have_rent'] = True
                initial_value['RentalCost'] = homerent_data[0].money                
            elif not home_owner.exists():
                initial_value['RentPermission'] = HomeRentPermission.no_permission            
                initial_value['IsNotBuyHome'] = True
            else:
                initial_value['RentPermission'] = HomeRentPermission.not_use

            form = ManualHomeRequestForm(initial = initial_value)

            context = {'form': form, 'user_form' : user_form}
            return render(request, self.template_name, context)
            
    def post(self, request, *args, **kwargs):        
        user = User.objects.get(PersonID = self.kwargs['person_id'])            
        # print('self.request.POST = ',self.request.POST)
        user_form = UserCurrentDataForm(self.request.POST, instance = user, prefix='user')
        user_form.save()
        home_request = ManualHomeRequestForm(self.request.POST)
        print('home_request.is_valid() =', home_request.is_valid())
        if home_request.is_valid():
            hr = home_request.save(commit=False)
            hr.recorder = self.request.user
            hr.ProcessStep = HomeRequestProcessStep.PERSON_PROCESS
            hr.PersonDateRecieved = date.today()
            if not hr.Comment : 
                hr.Comment = "กรอกโดยตรงจาก จนท.กพ.ทอ."
            hr.save()
            messages.success(self.request,f"บันทึกข้อมูล {hr.Requester.FullName} เรียบร้อย")
        else:
            print('form error =',home_request.errors)
        
        return redirect('HomeRequest:unitlist')


class ListHomeRequestView(AuthenUserTestMixin, ListView):
    allow_groups = ['PERSON_ADMIN']    
    # template_name = "Person/test.html"
    template_name = "Person/listManualHomeRequest.html"
    paginate_by = 25 

    def get_queryset(self):        
        self.home_request =  HomeRequest.objects.filter(year_round__Year = get_current_year()).order_by("-modified")
        return self.home_request



class ManualHomeRequestAPIView(AuthenUserTestMixin,APIView):
    allow_groups = ['PERSON_ADMIN']   
    def post(self, request):
        print('request.data = ',request.data)
        serializer = ManualHomeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(recorder = request.user)
        return HttpResponse('<script type="text/javascript">window.close(); window.parent.location.href = "/";</script>')


@login_required
def check_create_hr(request, person_id):
    allow_access = False
    for ag in ['PERSON_ADMIN']:
        if request.user.groups.filter(name=ag).exists():
            allow_access = True
            break
    if not allow_access:
        return JsonResponse({"status": "reject"})
               
    home_request = HomeRequest.objects.filter(year_round__Year = get_current_year()
                                     ).filter(Requester__PersonID = person_id)
    if home_request.exists():
        print("มีคำขอบ้านแล้ว")
        return JsonResponse({"status": "exists", "hr_id" : home_request[0].id })
    else:
        result = AddUserByPersonID(request, person_id)
        print(f"เพิ่ม User {person_id} แล้ว")
        print(result)
    
        return JsonResponse({"status": "new", "user" : result})


    
def SetNoHomeToHomeRequest():
    no_home_user_group = Group.objects.get(name='RTAF_NO_HOME_USER')
    for hm  in HomeRequest.current_year.all():
        requester = hm.Requester
        requester.groups.add(no_home_user_group)  
        requester.save()

            

