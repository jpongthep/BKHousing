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
from apps.Utility.utils import thai_date


def send_line_notify(notify_token, message):

    url = 'https://notify-api.line.me/api/notify'    
    headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer ' + notify_token}
    # msg = 'ทดสอบ ทดสอบ'
    r = rq.post(url, headers=headers, data = {'message' : message})
    # print(message)


#127.0.0.1:8000/hr/lnfy/

def armis_admin_notify():
    CurrentYearRound = YearRound.objects.filter(CurrentStep__in = ['RS','UP','PP'])
    year_round = CurrentYearRound[0] 

    Num_RP = Count('ProcessStep', filter = Q(ProcessStep = 'RP'))
    Num_RS = Count('ProcessStep', filter = Q(ProcessStep = 'RS'))
    Num_UP = Count('ProcessStep', filter = Q(ProcessStep = 'UP'))
    Num_US = Count('ProcessStep', filter = Q(ProcessStep = 'US'))
    Num_PP = Count('ProcessStep', filter = Q(ProcessStep = 'PP'))
    Num_GH = Count('ProcessStep', filter = Q(ProcessStep = 'GH'))

    homerequest = HomeRequest.objects.filter(year_round = year_round
                                    ).filter(ProcessStep__in = ['RP','RS','UP','US','PP','GH']   
                                    ).values('year_round'                             
                                    ).annotate(                                    
                                        Num_RP = Num_RP,
                                        Num_RS = Num_RS,                                   
                                        Num_UP = Num_UP,
                                        Num_US = Num_US,
                                        Num_GH = Num_GH,
                                        Num_PP = Num_PP,
                                        waited_doc = F('Num_RS') + F('Num_UP') + F('Num_US')                                        
                                    ).values('Num_RP','Num_RS', 'Num_UP', 'Num_US', 'Num_GH','Num_PP', YearRound = F('year_round__Year')
                                    ).exclude(Q(Num_RP = 0) & Q(Num_RS = 0) & Q(Num_UP = 0) & Q(Num_US = 0) & Q(Num_GH = 0)
                                    ).order_by("-Num_RS","-Num_UP","-Num_US","-waited_doc")

    # print(homerequest)
    if homerequest.exists():
        hm = homerequest[0]
        th_date = thai_date(date.today(),"wd-short")
        send_text = f"คำขอบ้านพักในระบบ ARMIS \n{th_date}\n\n"         
        send_text += f"- ขรก.ฯ กรอกคำขอ {hm['Num_RP']} เรื่อง\n" if hm['Num_RP'] > 0 else ""
        send_text += f"- รอ นขต. รับเรื่อง {hm['Num_RS']} เรื่อง\n" if hm['Num_RS'] > 0 else "- ไม่มีคำขอค้างรับ นขต.ฯ\n"
        send_text += f"- นขต. ดำเนินการ {hm['Num_UP']} เรื่อง\n" if hm['Num_UP'] > 0 else "- ไม่มีคำขอค้างดำเนินการ นขต.ฯ\n"
        send_text += f"- รอ กพ.ทอ. รับเรื่อง {hm['Num_US']} เรื่อง\n" if hm['Num_US'] > 0 else "- ไม่มีคำขอค้างรับ กพ.ฯ\n"
        send_text += f"- รอจัดสรร {hm['Num_PP']} เรื่อง\n\n" if hm['Num_PP'] > 0 else ""
        send_text += f"จัดสรรแล้ว {hm['Num_GH']} หลัง\n" if hm['Num_GH'] > 0 else ""
        
    else:
        send_text = "ไม่มีคำขอค้างในระบบ\n"

    send_text += f"https://armis.rtaf.mi.th"
    
    print(send_text)
    send_line_notify("klXrp9gFaCxXWZUfWoUNgr2UWF2DshKExui61zLbKno",send_text) #armis
    # send_line_notify("w3zHCgFDQcPVT2ApNBkGJplqUWHl8iPTL4PRM974Fx7",send_text) #docdogturoe


# @login_required
# @csrf_exempt
def unit_daily_notify(request = 0, pk = 0):
    if request:
        # messages.info(request,"ส่ง line notify เรียบร้อย")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))    
    if pk == 0:
        unit_notify_token = Unit.objects.filter(line_notify_token__isnull = False)
    else:
        unit_notify_token = Unit.objects.filter(id = pk)

    if not unit_notify_token.exists():
        return HttpResponse("ไม่มีข้อมูล Notify Token", content_type='text/html; charset=utf-8')
    
    CurrentYearRound = YearRound.objects.filter(CurrentStep__in = ['RS','UP','PP'])
    year_round = CurrentYearRound[0] 

    Num_RP = Count('ProcessStep', filter = Q(ProcessStep = 'RP'))
    Num_RS = Count('ProcessStep', filter = Q(ProcessStep = 'RS'))
    Num_UP = Count('ProcessStep', filter = Q(ProcessStep = 'UP'))
    Num_US = Count('ProcessStep', filter = Q(ProcessStep = 'US'))
    Num_PP = Count('ProcessStep', filter = Q(ProcessStep = 'PP'))
    Num_GH = Count('ProcessStep', filter = Q(ProcessStep = 'GH'))

    unit_list = []
    for notify_unit in unit_notify_token:

        homerequest = HomeRequest.objects.filter(Unit = notify_unit)
        unit_list.append(notify_unit.ShortName)
        homerequest = homerequest.filter(year_round = year_round
                                        ).filter(ProcessStep__in = ['RP','RS','UP','US','PP','GH']   
                                        ).values('Unit','sub_unit'
                                        ).annotate(                                    
                                            Num_RP = Num_RP,
                                            Num_RS = Num_RS,                                   
                                            Num_UP = Num_UP,
                                            Num_US = Num_US,
                                            Num_GH = Num_GH,
                                            Num_PP = Num_PP,
                                            waited_doc = F('Num_RP') + F('Num_RS') + F('Num_UP') + F('Num_US')                                        
                                        ).values('Num_RP','Num_RS', 'Num_UP', 'Num_US', 'Num_GH','Num_PP', UnitName = F('Unit__ShortName'), SubUnit = F('sub_unit')
                                        ).exclude(Q(Num_RP = 0) & Q(Num_RS = 0) & Q(Num_UP = 0) & Q(Num_US = 0) & Q(Num_GH = 0)
                                        ).order_by("SubUnit", "-Num_RS","-Num_UP","-Num_US","-Num_RP","-waited_doc")
        if homerequest.exists():
            th_date = thai_date(date.today(),"wd-short")
            send_text = f"คำขอค้างในระบบ {homerequest[0]['UnitName']}\n{th_date}\n\n"
            send_text += f""
            message_RP = message_RS = message_UP = message_US = message_PP = message_GH = ""

            for hm in homerequest:  

                print(hm)
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

                if hm['Num_PP'] > 0 :
                    if message_PP == "":
                        message_PP = f"รอ กพ.ทอ. จัดสรร\n"
                    message_PP += f" - {sub_unit} {hm['Num_PP']} เรื่อง\n"
            
                if hm['Num_GH'] > 0 :
                    if message_GH == "":
                        message_GH = f"ได้รับจัดสรรบ้านพักแล้ว\n"
                    message_GH += f" - {sub_unit} {hm['Num_GH']} หลัง\n"
            

            send_text +=  message_RP + message_RS + message_UP + message_US + message_GH
            send_text += "\n\nhttps://armis.rtaf.mi.th"
            send_line_notify(notify_unit.line_notify_token,send_text)
            # send_line_notify("ZHzsLE4ClkG0FT67R32ICR1whsUzXoKt800S9dUKUlU",send_text)
        else:
            send_text = "ไม่มีคำขอค้างในระบบ"
    
    if request:
        messages.info(request,"ส่ง line notify เรียบร้อย")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    # return HttpResponse(f"ส่ง Notify หน่วย {unit_list}", content_type='text/html; charset=utf-8')

# @login_required
# @csrf_exempt
def unit_new_allocate_notify(request = 0, pk = 0):

    if pk == 0:
        unit_notify_token = Unit.objects.filter(line_notify_token__isnull = False)
    else:
        unit_notify_token = Unit.objects.filter(id = pk)

    if not unit_notify_token.exists():
        return HttpResponse("ไม่มีข้อมูล Notify Token", content_type='text/html; charset=utf-8')
    
    CurrentYearRound = YearRound.objects.filter(CurrentStep__in = ['RS','UP','PP'])
    year_round = CurrentYearRound[0] 

    Num_GH = Count('ProcessStep', filter = Q(ProcessStep = 'GH'))

    unit_list = []
    for notify_unit in unit_notify_token:

        homerequest = HomeRequest.objects.filter(Unit = notify_unit).filter(lastest_allocate = True)
        unit_list.append(notify_unit.ShortName)
        homerequest = homerequest.filter(year_round = year_round
                                        ).filter(ProcessStep__in = ['GH']   
                                        ).values('Unit','sub_unit'
                                        ).annotate(                                    
                                            Num_GH = Num_GH,                                       
                                        ).values('Num_GH', UnitName = F('Unit__ShortName'), SubUnit = F('sub_unit')
                                        ).exclude(Q(Num_GH = 0)
                                        ).order_by("SubUnit")
        if homerequest.exists():
            th_date = thai_date(date.today(),"wd-short")
            send_text = f"ประกาศจัดสรรบ้านพักหน่วย {homerequest[0]['UnitName']}\n{th_date}\n\n"
            send_text += f""
            message_GH = ""

            for hm in homerequest:  

                print(hm)
                sub_unit = hm['SubUnit'].replace(hm['UnitName'], "ฯ") if hm['UnitName'] != hm['SubUnit'] else hm['UnitName']
                
                if hm['Num_GH'] > 0 :
                    message_GH += f" - {sub_unit} {hm['Num_GH']} หลัง\n"
            

            send_text +=  message_GH
            send_text += "\nข้าราชการสามารถตรวจสอบข้อมูลและ download แบบฟอร์มเพื่อการเข้าบ้านพักได้ที่ https://armis.rtaf.mi.th"
            # send_line_notify(notify_unit.line_notify_token,send_text)
            send_line_notify("ZHzsLE4ClkG0FT67R32ICR1whsUzXoKt800S9dUKUlU",send_text)
        
    if request:
        messages.info(request,"ส่ง line notify เรียบร้อย")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    # return HttpResponse(f"ส่ง Notify หน่วย {unit_list}", content_type='text/html; charset=utf-8')