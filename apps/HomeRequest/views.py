#python module
import os
from datetime import date, timedelta
import json
from io import StringIO, BytesIO
import logging
#django Module
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from django.conf import settings

from django.db.models import Q, F
from django.db.models import Count, Sum, Max

#3rd party module
# from rest_framework import viewsets
# from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

line_bot_api = LineBotApi('odFxpwpkdguKC7pxS5or45Ob358azEPO2Ysg4Ch0PhIYqXdM3Db0N8Q740pKGRCV9YH9SYKFSasYdSYFWYLSTglj8ze55KGhJa1yVWGHzO5DQC+2+8k0lCGljwwUolRCWPpllUeRA/qIWq6mnkaaxgdB04t89/1O/w1cDnyilFU=')
parser = WebhookParser('ab315a0889e1395ea1695fb0d8ea5790')

#My module
from .models import HomeRequest, CoResident
from .forms import HomeRequestForm, CoResidentFormSet
from apps.Utility.Constants import (YEARROUND_PROCESSSTEP, HomeRequestProcessStep,PERSON_STATUS, 
                                    HomeRentPermission, FINANCE_CODE)
from apps.UserData.models import Unit
from apps.Configurations.models import YearRound
from apps.UserData.forms import UserCurrentDataForm
from apps.UserData.models import User
from apps.Payment.models import FinanceData
from .serializers import HomeRequestSerializer
from apps.Utility.utils import decryp_file
logger = logging.getLogger('MainLog')

def get_current_year():
    CurrentYearRound = YearRound.objects.filter(CurrentStep__in = ['RS','UP','PP'])
    CurrentYear = CurrentYearRound[0].Year
    # print('CurrentYear = ',CurrentYear)
    return CurrentYear


class AuthenUserTestMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/login' 
    allow_groups = []
    # navigate_units = ['กพ.ทอ.','ยศ.ทอ.', 'ทสส.ทอ.','ขส.ทอ.', 'ศซว.ทอ.', 'รร.นนก.']

    def test_func(self):
        # if self.request.user.CurrentUnit.ShortName in self.navigate_units:
        #     for ag in self.allow_groups:
        #         if self.request.user.groups.filter(name=ag).exists():
        #             return True
        
        for ag in self.allow_groups:
            if self.request.user.groups.filter(name=ag).exists():
                return True
                
        if self.has_home_request():
            return True

        return False

    def has_home_request(self):
        queryset = HomeRequest.objects.filter(Requester = self.request.user)
        queryset = queryset.filter(year_round__Year = get_current_year())
        if queryset.exists():
            return queryset[0].id
        else:
            return False



class CreateHomeRequestView(AuthenUserTestMixin, CreateView):
    allow_groups = ['RTAF_NO_HOME_USER']
    model = HomeRequest
    form_class = HomeRequestForm
    template_name = "HomeRequest/CreateHomeRequest.html"

    # ทดสอบเพิ่มเติมว่าถ้าปีนี้มีการส่งคำขอแล้ว ก็ส่งอีกไม่ได้
    # def test_func(self):
    #     if super().test_func() == False:
    #         return False
    #     else:
    #         return not super().has_home_request()

    def get(self, request, *args, **kwargs):
        
        hr_id = super().has_home_request()
        if hr_id:
            print('Create get -> hr_id')
            return redirect('HomeRequest:update', pk = hr_id)

        self.object = None
        # form_class = self.get_form_class()
        # form = self.get_form(form_class)
        logger.info(f'{request.user.username} view HomeRequest Form')
        initial_value = {
                            'Rank': request.user.Rank,
                            'FullName': request.user.FullName,
                            'Position': request.user.Position,
                            'Unit': request.user.CurrentUnit,
                            'MobilePhone' : request.user.MobilePhone,
                            'OfficePhone' : request.user.OfficePhone,
                            'Unit' : request.user.CurrentUnit,
                            'sub_unit' : request.user.sub_unit,
                            'Salary' : request.user.current_salary,
                            'Status' : request.user.current_status,
                            'SpouseName' : request.user.current_spouse_name,
                            'SpousePID' : request.user.current_spouse_pid,
                            'IsHRISReport' : request.user.current_spouse_pid,
                            'Address' : request.user.Address
                        }       

        # เช็คข้อมูลการเบิก คชบ.ของตนเอง ในช่วง 6 เดือนล่าสุด
        homerent_data = FinanceData.objects.filter(PersonID =  request.user.PersonID
                                          ).filter(date__gte = date.today() - timedelta(days = 185)
                                          ).filter(code = FINANCE_CODE.HOMERENT
                                          ).filter(money__gt = 0
                                          ).order_by("money")
            
        # print('homerent_data',homerent_data)
        if(homerent_data.exists()):
            initial_value['RentPermission'] = HomeRentPermission.used
            initial_value['have_rent'] = True
            initial_value['RentalCost'] = homerent_data[0].money
        else:
            initial_value['RentPermission'] = HomeRentPermission.no_permission

        # ถ้ามีสถานภาพสมรส
        if(request.user.current_status in [PERSON_STATUS.MARRIES_TOGETHER, PERSON_STATUS.MARRIES_SEPARATE]):
            # เช็คข้อมูลการเบิก คชบ.ของคู่สมรส ในช่วง 6 เดือนล่าสุด
            homerent_data = FinanceData.objects.filter(PersonID =  request.user.current_spouse_pid
                                          ).filter(date__gte = date.today() - timedelta(days = 185)
                                          ).filter(code = FINANCE_CODE.HOMERENT
                                          ).filter(money__gt = 0
                                          ).order_by("money")
            if(homerent_data.exists()):
                initial_value['have_rent_spouse'] = True
                initial_value['RentalCostSpouse'] = homerent_data[0].money


        form = self.form_class(initial = initial_value, prefix='hr')

        co_resident_formset = CoResidentFormSet()

        initial_value = {
                            'OfficePhone' : request.user.OfficePhone,
                            'MobilePhone' : request.user.MobilePhone,
                            'RTAFEMail': request.user.username + '@rtaf.mi.th',
                        }        
        user_current_data_form =  UserCurrentDataForm(initial = initial_value, prefix='userdata')
        return self.render_to_response(
                                self.get_context_data(form=form,
                                                      co_resident_formset=co_resident_formset,
                                                      user_current_data_form = user_current_data_form
                                                        ))    

    # def get(self, request, *args, **kwargs):

    #     form = self.form_class(initial = initial_value)
    #     return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.form_class(request.POST, request.FILES, prefix='hr')

        user_current_data_form = UserCurrentDataForm(self.request.POST,instance = request.user, prefix='userdata')
        co_resident_formset = CoResidentFormSet(self.request.POST)
        if form.is_valid() and co_resident_formset.is_valid():
            return self.form_valid(form, user_current_data_form, co_resident_formset)
        else:
            return self.form_invalid(form, user_current_data_form, co_resident_formset)

    def form_valid(self, form, user_current_data_form, co_resident_formset):
        self.object = form.save(commit=False)
        # กำหนดค่าเริ่มต้นให้ form    
        self.object.Requester = self.request.user
        CurrentYearRound = YearRound.objects.filter(CurrentStep__in = ['RS','UP','PP'])

        self.object.year_round = CurrentYearRound[0]
        self.object.Unit = self.request.user.CurrentUnit
        self.object.save()
        
        user_current_data_form.save()

        co_resident = co_resident_formset.save(commit=False)
        for cr in co_resident:
            cr.home_request = self.object
            cr.save()

        if 'save' in self.request.POST:            
            self.object.ProcessStep = HomeRequestProcessStep.REQUESTER_PROCESS
            self.object.save()
            messages.success(self.request, f'เพิ่มข้อมูลบ้านพักของ {self.object.FullName} เรียบร้อย')
        elif 'send' in self.request.POST:
            self.object.update_process_step(
                                    HomeRequestProcessStep.REQUESTER_SENDED, 
                                    self.request.user)
            self.object.save()
            messages.success(self.request, f'บันทึกและส่งข้อมูลบ้านพักของ {self.object.FullName} เรียบร้อย')


        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, user_current_data_form, co_resident_formset):
        # print(form.errors)
        return self.render_to_response(
                 self.get_context_data(form=form,
                                       co_resident_formset=co_resident_formset,
                                       user_current_data_form = user_current_data_form
                                       )
        )


class UpdateHomeRequestView(AuthenUserTestMixin, UpdateView):
    allow_groups = ['RTAF_NO_HOME_USER']
    model = HomeRequest
    form_class = HomeRequestForm
    template_name = "HomeRequest/CreateHomeRequest.html"


    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.RequesterSended:
            return redirect('HomeRequest:af_person')

        home_request = self.object
        
        co_resident_formset = CoResidentFormSet(instance = home_request, 
                                                queryset = home_request.CoResident.order_by("Relation"))

        # print("UpdateHomeRequestView:get")
        

        return self.render_to_response(
                  self.get_context_data(form = HomeRequestForm(instance=self.object, prefix='hr'),
                                        user_current_data_form =  UserCurrentDataForm(instance = request.user, prefix='userdata'),
                                        co_resident_formset = co_resident_formset
                                        )
                                       )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        # print("UpdateHomeRequestView:get_context_data")

        if self.request.GET:
            # print('get_context_data:self.request.GET')
            data['form'] = HomeRequestForm(instance=self.object, prefix='hr')
            data["user_current_data_form"] = UserCurrentDataForm(instance = self.request.user, prefix='userdata')
            data["co_resident"] = CoResidentFormSet(instance=self.object)
        elif self.request.POST:
            # print('get_context_data:self.request.POST')
            data['form'] = HomeRequestForm(self.request.POST, prefix='hr')
            data["user_current_data_form"] = UserCurrentDataForm(self.request.POST, prefix='userdata')
            data["co_resident_formset"] = CoResidentFormSet(self.request.POST)
        return data

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance = self.object, prefix='hr')

        user_current_data_form = UserCurrentDataForm(self.request.POST, instance = request.user, prefix='userdata')
        co_resident_formset = CoResidentFormSet(self.request.POST, instance = self.object)

        # print('UpdateHomeRequestView:post:form.is_valid() ',form.is_valid())
        
        # print('UpdateHomeRequestView:post:user_current_data_form.is_valid() ',user_current_data_form.is_valid())
        # print('UpdateHomeRequestView:post:co_resident_formset.is_valid() ',co_resident_formset.is_valid())

        if form.is_valid() and user_current_data_form.is_valid() and co_resident_formset.is_valid():
            # print('co_resident_formset ', co_resident_formset)
            return self.form_valid(form, user_current_data_form, co_resident_formset)
        else:
            return self.form_invalid(form, user_current_data_form, co_resident_formset)

    def form_valid(self, form, user_current_data_form, co_resident_formset):

        # print('UpdateHomeRequestView:form_valid co_resident_formset = ',co_resident_formset)
        user_current_data_form.save()
        co_resident = co_resident_formset.save(commit=False)

        for cr in co_resident_formset.deleted_objects:
            cr.delete()

        for cr in co_resident:
            # print('coresident = ',cr)
            cr.home_request = self.object
            cr.save()

        if 'save' in self.request.POST:
            messages.warning(self.request, f'บันทึกการแก้ไขข้อมูลบ้านพักของ {self.object.FullName} เรียบร้อย *** ขั้นตอนการส่งยังไม่เรียบร้อย ***')
        elif 'send' in self.request.POST:
            self.object.update_process_step(
                                    HomeRequestProcessStep.REQUESTER_SENDED, 
                                    self.request.user)
            self.object.save()
            messages.success(self.request, f'บันทึกการแก้ไขและส่งข้อมูลบ้านพักของ {self.object.FullName} เรียบร้อย')

        return super().form_valid(form)

    def form_invalid(self, form, user_current_data_form, co_resident_formset):
        # print('UpdateHomeRequestView:form_invalid => user_current_data_form  ') #, user_current_data_form)
        # print('UpdateHomeRequestView:form_invalid => co_resident_formset => ') #, co_resident_formset)
        return super().form_invalid(form)

    def get_success_url(self):        
        return reverse('HomeRequest:af_person')


class AFPersonListView(AuthenUserTestMixin,ListView):
    template_name = "HomeRequest/af_person.html"
    allow_groups = ['RTAF_NO_HOME_USER']

    def get_queryset(self):
        queryset = HomeRequest.objects.filter(Requester = self.request.user)
        queryset = queryset.order_by("-year_round__Year")
        return queryset

    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)
        context['has_request'] = super().has_home_request(**kwargs)
        return context        


class HomeRequestUnitListView(AuthenUserTestMixin, ListView):
    model = HomeRequest    
    template_name = "HomeRequest/listVue.html"
    allow_groups = ['PERSON_ADMIN', 'PERSON_SUBUNIT_ADMIN', 'PERSON_UNIT_ADMIN']

    def split_sub_unit(self):
        user_unit = self.request.user.CurrentUnit
        sub_unit_list = str(user_unit.sub_unit_list)
        sub_unit_list = [x.strip() for x in sub_unit_list.split(",")]
        hr_queryset = HomeRequest.objects.filter(Unit = user_unit)
        for hr in hr_queryset:
            hr.sub_unit = hr.Unit.ShortName
            if not hr.Position:
                hr.save()
                continue

            match = next((x for x in sub_unit_list if x in hr.Position), False)
            print("#",hr.Position, match)
            if match:
                hr.sub_unit = match
            hr.save()

        user_queryset = User.objects.filter(CurrentUnit = user_unit)
        for user in user_queryset:
            user.sub_unit = user.CurrentUnit.ShortName
            if not user.Position:
                user.save() 
                continue

            match = next((x for x in sub_unit_list if x in user.Position), False)
            print("#",user.Position, match)
            if match:
                user.sub_unit = match
            user.save() 

        user_unit.re_cal_sub_unit = False
        user_unit.save()

    def get_queryset(self, *args, **kwargs):

        print('get_queryset')

        queryset = HomeRequest.objects.filter(year_round__Year = get_current_year())

        if self.request.user.CurrentUnit.re_cal_sub_unit:
            self.split_sub_unit()

        if self.request.user.groups.filter(name='PERSON_UNIT_ADMIN').exists():
                queryset = queryset.filter(Unit = self.request.user.CurrentUnit)              

        if self.request.user.groups.filter(name = 'PERSON_SUBUNIT_ADMIN').exists():
                queryset = queryset.filter(sub_unit = self.request.user.sub_unit ) 
        
        if 'unit_id' in self.kwargs:
            unit_id = self.kwargs['unit_id']
            if self.request.user.groups.filter(name='PERSON_ADMIN').exists():
                    queryset = queryset.filter(Unit_id = unit_id)
        
        queryset = queryset.order_by("-year_round__Year","ProcessStep","Requester__Rank")
        return queryset 
    
    def get_context_data(self, **kwargs):
        context = super(HomeRequestUnitListView, self).get_context_data(**kwargs)

        queryset = HomeRequest.objects.filter(year_round__Year = get_current_year())

        if self.request.user.groups.filter(Q(name='PERSON_UNIT_ADMIN') | Q(name = 'PERSON_SUBUNIT_ADMIN')).exists():
            queryset = queryset.filter(Unit = self.request.user.CurrentUnit)                


        if self.request.user.groups.filter(name = 'PERSON_SUBUNIT_ADMIN').exists():
            # print('get_context_data : ',self.request.user.sub_unit)

            queryset = queryset.filter(sub_unit = self.request.user.sub_unit ) 


        if 'unit_id' in self.kwargs:
            unit_id = self.kwargs['unit_id']
            if self.request.user.groups.filter(name='PERSON_ADMIN').exists():
                    queryset = queryset.filter(Unit_id = unit_id)

        Num_RP = Count('id', filter = Q(ProcessStep = 'RP'))
        Num_RS = Count('id', filter = Q(ProcessStep = 'RS'))
        Num_UP = Count('id', filter = Q(ProcessStep = 'UP'))
        Num_US = Count('id', filter = Q(ProcessStep = 'US'))
        Num_PPPA = Count('id', filter = Q(ProcessStep__in = ['PP','PA']))
        Num_GH = Count('id', filter = Q(ProcessStep = 'GH'))

        queryset = queryset.exclude(
                                    Q(ProcessStep = HomeRequestProcessStep.REQUESTER_CANCEL) 
                                ).values('Unit'
                                ).annotate(
                                    Num_RP = Num_RP,
                                    Num_RS = Num_RS,
                                    Num_UP = Num_UP,
                                    Num_US = Num_US,
                                    Num_PPPA = Num_PPPA,
                                    Num_GH = Num_GH
                                ).values(
                                    'Num_RP',
                                    'Num_RS',
                                    'Num_UP',
                                    'Num_US',
                                    'Num_PPPA',
                                    'Num_GH'
                                )
        # print('queryset = ',queryset)
        # print('queryset = ',queryset.query)

        context['hr'] = queryset[0]

        sub_unit_list = str(self.request.user.CurrentUnit.sub_unit_list)        
        sub_unit_list = [x.strip() for x in sub_unit_list.split(",")]
        context['sub_units'] = sub_unit_list
        return context
    

class HomeRequestAdminListView(HomeRequestUnitListView):
    model = HomeRequest    
    template_name = "Person/modal_list.html"
    allow_groups = ['PERSON_ADMIN']

    def get_queryset(self, *args, **kwargs):
        
        if 'unit_id' in self.kwargs:
            unit_id =  self.kwargs['unit_id']
            if self.request.user.groups.filter(name='PERSON_ADMIN').exists():
                    queryset = HomeRequest.objects.filter(Unit_id = unit_id)
        
        queryset = queryset.filter(year_round__Year = get_current_year())
        queryset = queryset.order_by("-year_round__Year")
        return queryset


class UnitList4PersonAdmin(AuthenUserTestMixin, APIView):
    allow_groups = ['PERSON_SUBUNIT_ADMIN', 'PERSON_UNIT_ADMIN','PERSON_ADMIN']

    def get(self, request, *args, **kwargs):        
        unit_id = kwargs["unit_id"] if kwargs.get("unit_id", None) is not None else request.user.Unit.id

        queryset = HomeRequest.objects.filter(Unit_id = unit_id).order_by("-ProcessStep","-PersonTroubleScore")
        queryset = queryset.filter(year_round__Year = get_current_year())
        if self.request.user.groups.filter(name = 'PERSON_SUBUNIT_ADMIN').exists():
            queryset = queryset.filter(sub_unit = self.request.user.sub_unit ) 
        serializer = HomeRequestSerializer(queryset, many=True)
        # print("serializer.data = ", serializer.data)
        return Response(serializer.data)


class HomeRequestUnitSummaryListView(AuthenUserTestMixin,ListView):
    # template_name = "Person/unit_summary.html"
    template_name = "Person/unit_summary_vue.html"
    allow_groups = ['PERSON_ADMIN']

    def get_queryset(self):

        Num_RP = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.REQUESTER_PROCESS))
        Num_RS = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.REQUESTER_SENDED))
        Num_UP = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.UNIT_PROCESS))
        Num_US = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.UNIT_SENDED))
        Num_PP = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.PERSON_PROCESS))
        Num_PA = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.PERSON_ACCEPTED))
        Num_GH = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.GET_HOUSE))
        DateSended = Max('UnitDateApproved')
        UnitApprover = Max('UnitApprover__first_name')
        
        queryset = HomeRequest.objects.filter(year_round__Year = get_current_year())

        queryset = queryset.exclude(
                                    Q(ProcessStep = HomeRequestProcessStep.REQUESTER_CANCEL) 
                                ).values('Unit'
                                ).annotate(
                                    DateSended = DateSended,
                                    UnitApprover = UnitApprover,
                                    Num_RP = Num_RP,
                                    Num_RS = Num_RS,
                                    Num_UP = Num_UP,
                                    Num_US = Num_US,
                                    Num_PP = Num_PP,
                                    Num_PA = Num_PA,
                                    Num_GH = Num_GH
                                ).values(
                                    'Unit',
                                    'Unit__ShortName',
                                    'DateSended',
                                    'UnitApprover',
                                    'Num_RP',
                                    'Num_RS',
                                    'Num_UP',
                                    'Num_US',
                                    'Num_PP',
                                    'Num_PA',
                                    'Num_GH'
                                )
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super(HomeRequestUnitSummaryListView, self).get_context_data(**kwargs)
        sub_unit_list = str(self.request.user.CurrentUnit.sub_unit_list)        
        sub_unit_list = [x.strip() for x in sub_unit_list.split(",")]
        context['sub_units'] = sub_unit_list
        return context


class HomeRequestDetail(AuthenUserTestMixin, DetailView):
    allow_groups = ['RTAF_NO_HOME_USER','PERSON_SUBUNIT_ADMIN', 'PERSON_UNIT_ADMIN']
    model = HomeRequest
    template_name = "HomeRequest/Detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(HomeRequestDetail, self).get_context_data(*args, **kwargs)            
        co_residence = CoResident.objects.filter(home_request=self.object).order_by("Relation")
        context["co_residence"] = co_residence
        return context


@login_required
def cancel_request(request, home_request_id):
    home_request = HomeRequest.objects.get(id = home_request_id)
    if request.user != home_request.Requester:
        raise PermissionDenied()
    else:
        if request.method == "POST":
            data = json.loads(request.body.decode("utf-8"))
            Comment = data["comment"]
            # print("data =  " ,Comment)
        home_request.cancel_request = True
        home_request.Comment = home_request.Comment + 'แจ้งยกเลิกคำขอเมื่อ ' + str(date.today()) + Comment
        home_request.save()
        return JsonResponse({"ok": True}, safe=False)
        
@login_required
def delete_hr(request, home_request_id):
    home_request = HomeRequest.objects.get(id = home_request_id)
    if request.user != home_request.Requester:
        raise PermissionDenied()
    else:
        home_request.delete()
        logger.info(request,'ลบคำขอบ้านพักเรียบร้อย')
        return JsonResponse({"ok": True}, safe=False)
    
               
@login_required
def update_process_step(request, home_request_id, process_step):
    allow_groups = ['PERSON_ADMIN','PERSON_SUBUNIT_ADMIN', 'PERSON_UNIT_ADMIN']
    allow_access = False
    for ag in allow_groups:
        if request.user.groups.filter(name=ag).exists():
            allow_access = True
            break
    if not allow_access:
        raise PermissionDenied()
               
    home_request = HomeRequest.objects.get(id = home_request_id)
    home_request.ProcessStep = process_step
    if process_step == 'RP':
        home_request.RequesterDateSend = None
        home_request.RequesterDateSend = None
        home_request.UnitReciever = None
        home_request.UnitDateRecieved = None
        home_request.UnitApprover = None
        home_request.cancel_request = False
        home_request.PersonReciever = None
        home_request.PersonDateRecieved = None
        home_request.PersonApprover = None
        home_request.PersonDateApproved = None
        home_request.IsUnitEval = False
        home_request.UnitTroubleScore = None
        home_request.IsPersonEval = False
        home_request.TroubleScore = None
    home_request.save()
    home_request.update_process_step(process_step, request.user)
    


    # if process_step == HomeRequestProcessStep.REQUESTER_PROCESS:
    #     messages.info(request,f'บันทึกขั้นตอนคำขอบ้าน {home_request.Requester.FullName} เรียบร้อย')
    #     return HttpResponseRedirect("/hr/list")
    if process_step in [HomeRequestProcessStep.REQUESTER_PROCESS,
                          HomeRequestProcessStep.UNIT_PROCESS,
                         HomeRequestProcessStep.UNIT_SENDED,
                         HomeRequestProcessStep.PERSON_PROCESS, 
                         HomeRequestProcessStep.PERSON_ACCEPTED]:
        return JsonResponse({"success": True})
    elif process_step == HomeRequestProcessStep.REQUESTER_CANCEL:
        return HttpResponseRedirect("/hr/list")


@csrf_exempt
def homerequest_detail(request, username):
    try:
        user = User.objects.get(username = username)     
        CurrentYearRound = YearRound.objects.filter(CurrentStep__in = ['RS','UP','PP'])
        year_round = CurrentYearRound[0] 
        homerequest = HomeRequest.objects.filter(year_round = year_round).filter(Requester = user)
    except User.DoesNotExist:
        dump = json.dumps({'status': 'username not found'})            
        return HttpResponse(dump, content_type='application/json')

    # print('homerequest',homerequest)
    if not homerequest.exists():
        dump = json.dumps({'status': 'hr not found'})            
        return HttpResponse(dump, content_type='application/json')

    if request.method == 'GET':
        serializer = HomeRequestSerializer(homerequest[0])
        return JsonResponse(serializer.data)
