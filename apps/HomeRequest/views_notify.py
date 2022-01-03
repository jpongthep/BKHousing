#python module
import os
from datetime import date, timedelta
import json
from io import StringIO, BytesIO
import logging
import requests as rq
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

#My module
from .models import HomeRequest, CoResident
from apps.UserData.models import Unit
from apps.Configurations.models import YearRound



def send_line_notify(notify_token, message):

    url = 'https://notify-api.line.me/api/notify'    
    headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer ' + notify_token}
    msg = 'ทดสอบ ทดสอบ'
    # r = rq.post(url, headers=headers, data = {'message' : message})
    print(message)

@login_required
# @csrf_exempt
def unit_daily_notify(request):

    unit_notify_token = Unit.objects.filter(line_notify_token__isnull = False)
    if not unit_notify_token.exists():
        return HttpResponse("ไม่มีข้อมูล Notify Token", content_type='text/html; charset=utf-8')
    
    CurrentYearRound = YearRound.objects.filter(CurrentStep__in = ['RS','UP','PP'])
    year_round = CurrentYearRound[0] 

    Num_RP = Count('ProcessStep', filter = Q(ProcessStep = 'RP'))
    Num_RS = Count('ProcessStep', filter = Q(ProcessStep = 'RS'))
    Num_UP = Count('ProcessStep', filter = Q(ProcessStep = 'UP'))
    Num_US = Count('ProcessStep', filter = Q(ProcessStep = 'US'))

    unit_list = []
    for notify_unit in unit_notify_token:

        homerequest = HomeRequest.objects.filter(Unit = notify_unit)
        unit_list.append(notify_unit.ShortName)
        homerequest = homerequest.filter(year_round = year_round
                                        ).filter(ProcessStep__in = ['RP','RS','UP','US']   
                                        ).values('Unit','sub_unit'
                                        ).annotate(                                    
                                            Num_RP = Num_RP,
                                            Num_RS = Num_RS,                                   
                                            Num_UP = Num_UP,
                                            Num_US = Num_US,
                                            waited_doc = F('Num_RP') + F('Num_RS') + F('Num_UP') + F('Num_US')                                        
                                        ).values('Num_RP','Num_RS', 'Num_UP', 'Num_US', UnitName = F('Unit__ShortName'), SubUnit = F('sub_unit')
                                        ).exclude(Q(Num_RP = 0) & Q(Num_RS = 0) & Q(Num_UP = 0) & Q(Num_US = 0)
                                        ).order_by("SubUnit", "-Num_RS","-Num_UP","-Num_US","-Num_RP","-waited_doc")
        if homerequest.exists():

            send_text = f"คำขอค้างในระบบ {homerequest[0]['UnitName']}\n{date.today().strftime('%d-%m-%y')}\n\n"
            send_text += f""
            message_RP = message_RS = message_UP = message_US = ""

            for hm in homerequest:  

                sub_unit = hm['SubUnit'].replace(hm['UnitName'], "ฯ") if hm['UnitName'] != hm['SubUnit'] else hm['UnitName']
                if hm['Num_RP'] > 0 :
                    if message_RP == "":
                        message_RP = f"ขรก.ฯ กรอกคำขอ \n"
                    message_RP += f" - {sub_unit} {hm['Num_RP']} เรื่อง\n"
                    
                if hm['Num_RS'] > 0 :
                    if message_RS == "":
                        message_RS = f"รอ นขต.{hm['UnitName']} รับเรื่อง\n"
                    message_RS += f" - {sub_unit} {hm['Num_RS']} เรื่อง\n"

                if hm['Num_UP'] > 0 :
                    if message_UP == "":
                        message_UP = f"รอ นขต.{hm['UnitName']} ดำเนินการ\n"
                    message_UP += f" - {sub_unit} {hm['Num_UP']} เรื่อง\n"

                if hm['Num_US'] > 0 :
                    if message_US == "":
                        message_US = f"รอ กพ.ทอ. รับเรื่อง\n"
                    message_US += f" - {sub_unit} {hm['Num_US']} เรื่อง\n"
            

            send_text +=  message_RP + message_RS + message_UP + message_US
            # send_line_notify(notify_unit.line_notify_token,send_text)
            send_line_notify("klXrp9gFaCxXWZUfWoUNgr2UWF2DshKExui61zLbKno",send_text)
        else:
            send_text = "ไม่มีคำขอค้างในระบบ"
    
    return HttpResponse(f"ส่ง Notify หน่วย {unit_list}", content_type='text/html; charset=utf-8')