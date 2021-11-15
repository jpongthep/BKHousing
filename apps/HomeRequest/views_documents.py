#python module
import os
from datetime import date, timedelta
import json
from io import StringIO, BytesIO
import logging
#django Module
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,  HttpResponseBadRequest, HttpResponseForbidden
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.conf import settings

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from openpyxl import load_workbook

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

line_bot_api = LineBotApi('odFxpwpkdguKC7pxS5or45Ob358azEPO2Ysg4Ch0PhIYqXdM3Db0N8Q740pKGRCV9YH9SYKFSasYdSYFWYLSTglj8ze55KGhJa1yVWGHzO5DQC+2+8k0lCGljwwUolRCWPpllUeRA/qIWq6mnkaaxgdB04t89/1O/w1cDnyilFU=')
parser = WebhookParser('ab315a0889e1395ea1695fb0d8ea5790')

#My module
from .models import HomeRequest
from .views import get_current_year
from apps.UserData.models import Unit
from apps.Utility.utils import decryp_file
logger = logging.getLogger('MainLog')
evidence_logger = logging.getLogger('EvidenceAccessLog')


def ArabicToThai(number_string): 
    dic = { 
        '0':'๐', 
        '1':'๑', 
        '2':'๒', 
        '3':'๓', 
        '4':'๔', 
        '5':'๕', 
        '6':'๖', 
        '7':'๗', 
        '8':'๘', 
        '9':'๙', 
    }
    result = ""
    for ch in number_string:
        if ch in "0123456789":
            result += dic[ch]
        else:
            result += ch
    
    return result

month_text = ["","ม.ค.","ก.พ.","มี.ค.","เม.ย.","พ.ค.","มิ.ย.","ก.ค.","ส.ค.","ก.ย.","ต.ค.","พ.ย.","ธ.ค."]
full_month_text = ["","มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","มิถุนายน","กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"]


def TestDocument(request, home_request_id):
    # testdoc = static('documents/test_doc.docx')
    home_request = HomeRequest.objects.get(id = home_request_id)

    # if home_request.ProcessStep == 'RP':
    #     testdoc =  os.path.join(settings.TEMPLATES[0]['DIRS'][0],'documents/house_request_data_1_page_draft.docx')
    #     docx_title= f"Draft-{home_request.Requester.AFID}.docx"
    # else:
    testdoc =  os.path.join(settings.TEMPLATES[0]['DIRS'][0],'documents/house_request_data_1_page.docx')
    docx_title= f"House-{home_request.Requester.AFID}.docx"

    document = Document(testdoc)

    self_call = "กระผม" if home_request.Requester.Sex == "ชาย" else "ดิฉัน"
    SpouseName = home_request.SpouseName if home_request.SpouseName else ""

    
    Salary = int(home_request.Salary) if home_request.Salary is not None else "0"
    add_salary = int(home_request.AddSalary) if home_request.AddSalary is not None else "0"

    Income = int(Salary) + int(add_salary)
    
    RentalCost = ""
    if home_request.RentPermission == 1:
        Z1, Z2, Z3 = "X", "  ", "  "
    elif home_request.RentPermission == 2:
        Z1, Z2, Z3 = "  ", "X", "  "
    elif home_request.RentPermission == 3:
        Z1, Z2, Z3 = "  ", "X", "X"
        RentalCost = home_request.RentalCost  if home_request.RentalCost is not None else 0
        RentalCost = "{:,} บาท".format(RentalCost)
    
    if home_request.have_rent_spouse:
        ZK = "X"
        WifeRentalCost = home_request.RentalCostSpouse if home_request.RentalCostSpouse  is not None  else 0
        WifeRentalCost = "{:,} บาท".format(WifeRentalCost)        
    else:
        ZK = "  "
        WifeRentalCost = " -"  

    IsNotRTAFHome = "--"
    status_description = ""
    if home_request.Status in [2, 7]: # ถ้าสถานะเป็นสมรส
        IsNotRTAFHome = "X" if home_request.IsNotRTAFHome else "  "
        SpouseName = "{}".format(SpouseName)
        status_description = "มีสถานภาพสมรส"
        family_single = "ครอบครัว"
    elif  home_request.Status == 1:
        status_description = "มีสถานภาพโสด"
        family_single = "โสด"
    else:
        ZK = "--"
        SpouseName = " - "
        family_single = "ครอบครัว"

    IsNotBuyHome = "X" if home_request.IsNotBuyHome else "  "
    IsNotOwnHome = "X" if home_request.IsNotOwnHome else "  "
    IsNeverRTAFHome = "X" if home_request.IsNeverRTAFHome else "  "
    ImportanceDuty = "X" if home_request.ImportanceDuty else "  "
    IsMoveFromOtherUnit = "X" if home_request.IsMoveFromOtherUnit else "  "
    IsHomelessEvict = "X" if home_request.IsHomelessEvict else "  "
    ContinueHouse = "X" if home_request.ContinueHouse else "  "
    IsHomelessDisaster = "X" if home_request.IsHomelessDisaster else "  "
    OtherTrouble = "X" if home_request.OtherTrouble else "  "
    IsHomeNeed = "X" if home_request.IsHomeNeed else "  "
    IsFlatNeed = "X" if home_request.IsFlatNeed else "  "
    IsShopHouseNeed = "X" if home_request.IsShopHouseNeed else "  "
    type_need = ""
    type_need = "บ้าน น." if home_request.IsHomeNeed else ""
    type_need += " แฟลต" if home_request.IsFlatNeed else ""
    type_need += " เรือนแถว" if home_request.IsShopHouseNeed else ""
    NumResidence = home_request.CoResident.all().count()
    NumResidence = "-" if NumResidence == 0 else NumResidence

    HouseRegistration = "X" if home_request.HouseRegistration else "  "
    MarriageRegistration = "X" if home_request.MarriageRegistration else "  "
    SpouseApproved = "X" if home_request.SpouseApproved else "  "
    DivorceRegistration = "X" if home_request.DivorceRegistration else "  "
    SpouseDeathRegistration = "X" if home_request.SpouseDeathRegistration else "  "

    the_day = home_request.RequesterDateSend if home_request.RequesterDateSend != None else home_request.modified
    Day = the_day.day if the_day != None else the_day.day
    Month = month_text[the_day.month] if the_day != None else month_text[the_day.day]
    Year =  str((the_day.year + 543) % 100) if the_day != None else str((the_day.day + 543) % 100) 

    PR1 = home_request.get_ZoneRequestPriority1_display() if home_request.ZoneRequestPriority1 else ""
    PR2 = home_request.get_ZoneRequestPriority2_display() if home_request.ZoneRequestPriority2 else ""
    PR3 = home_request.get_ZoneRequestPriority3_display() if home_request.ZoneRequestPriority3 else ""
    PR4 = home_request.get_ZoneRequestPriority4_display() if home_request.ZoneRequestPriority4 else ""
    PR5 = home_request.get_ZoneRequestPriority5_display() if home_request.ZoneRequestPriority5 else ""
    PR6 = home_request.get_ZoneRequestPriority6_display() if home_request.ZoneRequestPriority6 else ""

    zone_order_list = [PR1,PR2,PR3,PR4,PR5,PR6]
    zone_order_list = [zone for zone in zone_order_list if zone != ""]
    zone_order = ", ".join(zone_order_list)

    Rank = "{}".format(home_request.Requester.get_Rank_display())
    if "ว่าที่" in Rank:
        Rank = Rank[7:]
    FullName = home_request.FullName
    if "ว่าที่" in FullName:
        FullName = FullName[7:]
    dic = {
            'Sex': self_call,
            'Rank': Rank,
            'FullName':FullName,
            'PersonID':home_request.Requester.PersonID,
            'Position':home_request.Position,
            'ADDR':home_request.Address,
            'GPC':home_request.GooglePlusCodes1,
            'Distance': str(home_request.distance),
            'UnitFN':home_request.Unit.FullName,
            'UnitSN':home_request.Unit.ShortName,
            'OfficePhone':home_request.Requester.OfficePhone,
            'MobilePhone':home_request.Requester.MobilePhone,
            'Income': "{:,}".format(Income),
            'Status':"{}".format(home_request.get_Status_display()),
            'status_description':status_description,
            'family_single':family_single,
            'type_need':type_need,
            'zone_order':zone_order,
            'SpouseName': SpouseName,
            'RequesterDateSend ': f"{Day} {Month}{Year}",
            'Z1':Z1,
            'Z2':Z2,
            'Z3':Z3,
            'WifeRentalCost':WifeRentalCost,
            'RentalCost' : RentalCost,
            'Z4':IsNotBuyHome,
            'Z5':IsNotOwnHome,
            'Z6':IsNeverRTAFHome,
            'Z7':IsNotRTAFHome,
            'Z8':ImportanceDuty,
            'Z9':IsMoveFromOtherUnit,
            'ZA':IsHomelessEvict,
            'ZB':IsHomelessDisaster,
            'ZC':IsHomeNeed,
            'ZD':IsFlatNeed,
            'ZE':IsShopHouseNeed,
            'ZF':HouseRegistration,
            'ZG':MarriageRegistration,
            'ZH':SpouseApproved,
            'ZI':DivorceRegistration,
            'ZJ':SpouseDeathRegistration,
            'ZK':ZK,
            'ZX':ContinueHouse,
            'ZY':OtherTrouble,
            'PR1': PR1,
            'PR2': PR2,
            'PR3': PR3,
            'PR4': PR4,
            'PR5': PR5,
            'PR6': PR6,
            'Residence' : str(NumResidence),
            'Month': Month,
            'Year':Year
            }
    # print(dic)
    
    for para in document.paragraphs:
        # print('para = ',para)
        for key, value in dic.items():
            if key in para.text:
                inline = para.runs
                # print('inline = ',inline)
                # Loop added to work with runs (strings with same style)
                for i in range(len(inline)):
                    if key in inline[i].text:
                        if value: # ถ้ามีการกรอกข้อมูล
                            Value = ArabicToThai(value) if key != 'GPC' else value
                        else: # ถ้าไม่มีการกรอกข้อมูล
                            Value = ""
                        text = inline[i].text.replace(key, Value)
                        inline[i].text = text

    # Prepare document for download        
    # -----------------------------
    f = BytesIO()
    document.save(f)
    length = f.tell()
    f.seek(0)
    response = HttpResponse(
        f.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    # print('docx_title = ',docx_title)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(docx_title)
    response['Content-Length'] = length
    return response

def UnitReportDocument(request, Unit_id):
    # testdoc = static('documents/test_doc.docx')
    home_request = HomeRequest.objects.filter(Unit_id = Unit_id)

    testdoc =  os.path.join(settings.TEMPLATES[0]['DIRS'][0],'documents/house_request_unit.docx')
    docx_title= f"Unit-{Unit_id}.docx"

    document = Document(testdoc)

    Month = month_text[date.today().month]
    Year =  str((date.today().year + 543) % 100)

    dic = {
            'UnitSN': request.user.CurrentUnit.ShortName,
            'OfficePhone':request.user.OfficePhone,
            'Num_US' : "5",
            'Month': Month,
            'Year':Year
            }
    # print(dic)
    
    for para in document.paragraphs:
        # print('para = ',para)
        for key, value in dic.items():
            if key in para.text:
                inline = para.runs
                # print('inline = ',inline)
                # Loop added to work with runs (strings with same style)
                for i in range(len(inline)):
                    if key in inline[i].text:
                        if value: # ถ้ามีการกรอกข้อมูล
                            Value = ArabicToThai(value) if key != 'GPC' else value
                        else: # ถ้าไม่มีการกรอกข้อมูล
                            Value = ""
                        text = inline[i].text.replace(key, Value)
                        inline[i].text = text

    # Prepare document for download        
    # -----------------------------
    f = BytesIO()
    document.save(f)
    length = f.tell()
    f.seek(0)
    response = HttpResponse(
        f.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    # print('docx_title = ',docx_title)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(docx_title)
    response['Content-Length'] = length
    return response

def ConsentForm(request):
    testdoc =  os.path.join(settings.TEMPLATES[0]['DIRS'][0],'documents/letter_of_consent.docx')
    docx_title= f"consentform.docx"
    
    document = Document(testdoc)

    spname = request.POST.get("if_spouse_name","")
    address = request.POST.get("if_address","")

    spouse = "ภรรยา" if request.user.Sex == "ชาย" else "สามี"
    selfcall = "สามี" if request.user.Sex == "ชาย" else "ภรรยา"

    day = str(date.today().day)
    month = full_month_text[date.today().month]
    year =  str((date.today().year + 543))

    dic = {
            'spouse': spouse,            
            'selfcall': selfcall,            
            'spname': spname,            
            'address': address,            
            'username':request.user.FullName,
            'day' : day,
            'month' : month,
            'year' : year,
            }

    for para in document.paragraphs:
        # print('para = ',para)
        for key, value in dic.items():
            if key in para.text:
                inline = para.runs
                # print('inline = ',inline)
                # Loop added to work with runs (strings with same style)
                for i in range(len(inline)):
                    if key in inline[i].text:
                        if value: # ถ้ามีการกรอกข้อมูล
                            Value = ArabicToThai(value) if key != 'GPC' else value
                        else: # ถ้าไม่มีการกรอกข้อมูล
                            Value = ""
                        text = inline[i].text.replace(key, Value)
                        inline[i].text = text


    f = BytesIO()
    document.save(f)
    length = f.tell()
    f.seek(0)
    response = HttpResponse(
        f.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    # print('docx_title = ',docx_title)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(docx_title)
    response['Content-Length'] = length
    return response

 
def TestExcel(request,unit_id):
    # testdoc = static('documents/test_doc.docx')
    testxls =  os.path.join(settings.TEMPLATES[0]['DIRS'][0],'documents/unit_report.xlsx')
    # Start by opening the spreadsheet and selecting the main sheet
    workbook = load_workbook(filename=testxls)
    xls_title= f"unit_report.xlsx"

    sheet = workbook.active

    # Write what you want into a specific cell
    sheet["A1"] = f'หน่วย {request.user.CurrentUnit.ShortName}'

    
    xls_unit = Unit.objects.get(id = unit_id)

    queryset = HomeRequest.objects.filter(Unit = xls_unit
                                 ).filter(ProcessStep = 'US'
                                 ).filter(year_round__Year = get_current_year()
                                 ).order_by("Requester__Rank")
    first_row = 6
    for i, data in enumerate(queryset):
        Salary = data.Salary if data.Salary else 0
        AddSalary = data.AddSalary if data.AddSalary else 0
        Income = "{:,}".format(Salary + AddSalary)
        sheet[f"A{first_row+i}"] = i+1
        sheet[f"B{first_row+i}"] = data.FullName
        sheet[f"C{first_row+i}"] = data.get_Status_display()
        sheet[f"D{first_row+i}"] = ArabicToThai(Income)
        sheet[f"R{first_row+i}"] = ArabicToThai(data.Requester.MobilePhone)

    f = BytesIO()
    
    workbook.save(f)
    length = f.tell()
    f.seek(0)
    response = HttpResponse(
        f.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    # print('xls = ',xls_title)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(xls_title)
    response['Content-Length'] = length
    return response

@csrf_exempt
def line_api(request):
    # Chanel ID = 1656623264
    # Channel secret ab315a0889e1395ea1695fb0d8ea5790
    # Channel access token (long-lived) = odFxpwpkdguKC7pxS5or45Ob358azEPO2Ysg4Ch0PhIYqXdM3Db0N8Q740pKGRCV9YH9SYKFSasYdSYFWYLSTglj8ze55KGhJa1yVWGHzO5DQC+2+8k0lCGljwwUolRCWPpllUeRA/qIWq6mnkaaxgdB04t89/1O/w1cDnyilFU=
    print("function access")
    if request.method == 'POST':
        dump = json.dumps({'type': 'text', 'text': 'armis สวัสดีครับ'})            
        return HttpResponse(dump, content_type='application/json')    
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                if isinstance(event.message, TextMessage):
                    try:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=event.message.text)
                        )
                    except LineBotApiError as e:
                        print("1: ",e.status_code)
                        print("2: ",e.error.message)
                        print("3: ",e.error.details)

        dump = json.dumps({'type': 'text', 'text': 'armis สวัสดีครับ'})            
        return HttpResponse(dump, content_type='application/json')            
    else:
        if request.method == 'GET':
            dump = json.dumps({'type': 'text', 'text': 'armis สวัสดีครับ'})            
            return HttpResponse(dump, content_type='application/json')    
        
from django.conf import settings
from django.http import HttpResponse, Http404
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter

@login_required
def download_decryp(request, hr_id, evidence):
    try:
        home_request = HomeRequest.objects.get(id = hr_id)
    except:
        raise Http404

    def evd_enc(evd,hr_field):
        if hr_field:
            return evd, str(hr_field)
        else:
            raise Http404

    if evidence == 'HR':
        evidence, encryp_file = evd_enc('HouseRegistration', home_request.HouseRegistration)        
    elif evidence == 'MR':
        evidence, encryp_file = evd_enc('MarriageRegistration',home_request.MarriageRegistration)        
    elif evidence == 'SA':
        evidence, encryp_file = evd_enc('SpouseApproved',home_request.SpouseApproved)        
    elif evidence == 'DR':
        evidence, encryp_file = evd_enc('DivorceRegistration',home_request.DivorceRegistration)        
    elif evidence == 'SD':
        evidence, encryp_file = evd_enc('SpouseDeathRegistration',home_request.SpouseDeathRegistration)        
    else:
        raise Http404

    # ผู้เข้าดูเอกสารได้มี 
    #   1. เจ้าของเอกสาร
    #   2. Admin ของหน่วยผู้ส่ง 
    #   3. Admin กพ.ทอ.
    allow_access = False
    access_type = ""
    if home_request.Requester.id == request.user.id:
        access_type = "Self Access, "
        allow_access = True
    if request.user.groups.filter(name='PERSON_UNIT_ADMIN').exists():
        if request.user.CurrentUnit == home_request.Unit:
            access_type += "Unit ADMIN Access, "
            allow_access = True
    if request.user.groups.filter(name='PERSON_ADMIN').exists():
        access_type += "Person ADMIN Access "
        allow_access = True

    if not allow_access: raise PermissionDenied()

    file_path = os.path.join(settings.MEDIA_ROOT, encryp_file)
    watermark_file = os.path.join(settings.TEMPLATES[0]['DIRS'][0],'documents/watermark.pdf')

    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            if ".enc" in encryp_file:
                data_decryp_file = decryp_file(fh.read())
            else:
                data_decryp_file = fh.read()
            
            data_decryp_file_byte_io = BytesIO(data_decryp_file)

            if not "Self" in access_type:
                input_pdf = PdfFileReader(data_decryp_file_byte_io)
                watermark_pdf = PdfFileReader(watermark_file)
                watermark_page = watermark_pdf.getPage(0)

                output = PdfFileWriter()

                for i in range(input_pdf.getNumPages()):
                    pdf_page = input_pdf.getPage(i)
                    # pdf_page = watermark_page
                    # pdf_page.mergePage(input_pdf.getPage(i))
                    pdf_page.mergePage(watermark_page)
                    output.addPage(pdf_page)
                
                merged_file = BytesIO()
                output.write(merged_file)

                # length = merged_file.tell()
                merged_file.seek(0)

                data_decryp_file = merged_file.getvalue()

            evidence_logger.info(f'{home_request.Requester.username} {evidence} access by {request.user.username} ({access_type})')
            response = HttpResponse(data_decryp_file, content_type="application/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404