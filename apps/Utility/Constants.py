from django.db import models
from django.utils.translation import gettext_lazy as _

USER_PERMISSION = (
    ("RTAF_NO_HOME_USER", "RTAF_no_home_user"),
    ("RTAF_HOME_USER", "RTAF_home_user"),
    ("PERSON_UNIT_USER", "Person_unit_user"),
    ("PERSON_ADMIN", "Person_admin"),
    ("HOME_EXAMINE_OFFICER", "Home_examine_officer"),
    ("MP_OFFICER", "MP_officer"),
    ("FINANCIAL_OFFICER", "Financial_officer"),
    ("CIVIL_OFFICER", "Civil_officer"),
)

CHOICE_Rank = (
    ( 30101 ,  'พล.อ.อ.*' ) ,
    ( 30102 ,  'พล.อ.อ.*หญิง' ) ,
    ( 30211 ,  'พล.อ.อ.' ) ,
    ( 30212 ,  'พล.อ.อ.หญิง' ) ,
    ( 30221 ,  'พล.อ.ท.' ) ,
    ( 30222 ,  'พล.อ.ท.หญิง' ) ,
    ( 30231 ,  'พล.อ.ต.' ) ,
    ( 30232 ,  'พล.อ.ต.หญิง' ) ,
    ( 30301 ,  'น.อ.(พ)' ) ,
    ( 30302 ,  'น.อ.(พ) หญิง' ) ,
    ( 30411 ,  'น.อ.' ) ,
    ( 30412 ,  'น.อ.หญิง' ) ,
    ( 30421 ,  'น.ท.' ) ,
    ( 30422 ,  'น.ท.หญิง' ) ,
    ( 30431 ,  'น.ต.' ) ,
    ( 30432 ,  'น.ต.หญิง' ) ,
    ( 30511 ,  'ร.อ.' ) ,
    ( 30512 ,  'ร.อ.หญิง' ) ,
    ( 30521 ,  'ร.ท.' ) ,
    ( 30522 ,  'ร.ท.หญิง' ) ,
    ( 30531 ,  'ร.ต.' ) ,
    ( 30532 ,  'ร.ต.หญิง' ) ,
    ( 30541 ,  'กห.ส.' ) ,
    ( 30542 ,  'กห.ส.หญิง' ) ,
    ( 30611 ,  'พ.อ.อ.(พ)' ) ,
    ( 30612 ,  'พ.อ.อ.(พ) หญิง' ) ,
    ( 30711 ,  'พ.อ.อ.' ) ,
    ( 30712 ,  'พ.อ.อ.หญิง' ) ,
    ( 30721 ,  'พ.อ.ท.' ) ,
    ( 30722 ,  'พ.อ.ท.หญิง' ) ,
    ( 30731 ,  'พ.อ.ต.' ) ,
    ( 30732 ,  'พ.อ.ต.หญิง' ) ,
    ( 30811 ,  'จ.อ.' ) ,
    ( 30812 ,  'จ.อ.หญิง' ) ,
    ( 30821 ,  'จ.ท.' ) ,
    ( 30822 ,  'จ.ท.หญิง' ) ,
    ( 30831 ,  'จ.ท.' ) ,
    ( 30832 ,  'จ.ต.หญิง' ) ,
    ( 30841 ,  'กห.ป.' ) ,
    ( 30842 ,  'กห.ป.หญิง' ) ,
    ( 31411 ,  'ว่าที่ น.อ.' ) ,
    ( 31412 ,  'ว่าที่ น.อ.หญิง' ) ,
    ( 31421 ,  'ว่าที่ น.ท.' ) ,
    ( 31422 ,  'ว่าที่ น.ท.หญิง' ) ,
    ( 31431 ,  'ว่าที่ น.ต.' ) ,
    ( 31432 ,  'ว่าที่ น.ต.หญิง' ) ,
    ( 31511 ,  'ว่าที่ ร.อ.' ) ,
    ( 31512 ,  'ว่าที่ ร.อ.หญิง' ) ,
    ( 31521 ,  'ว่าที่ ร.ท.' ) ,
    ( 31522 ,  'ว่าที่ ร.ท.หญิง' ) ,
    ( 31531 ,  'ว่าที่ ร.ต.' ) ,
    ( 31532 ,  'ว่าที่ ร.ต.หญิง' ) ,
    ( 40200 ,  'พนง.อาวุโสหญิง' ) ,
    ( 40201 ,  'พนง.อาวุโส' ) ,
    ( 40400 ,  'พนง.หญิง' ) ,
    ( 40401 ,  'พนง.' ) ,
    ( 0 ,  '' )
) 

# ขั้นตอนการปฏิบัติใน 1 วงรอบ

class YEARROUND_PROCESSSTEP(models.TextChoices):
    NOT_OPEN = 'NO', _('NotOpen')
    REQUEST_SENDED = 'RS', _('RequestSended')
    UNIT_PROCESS = 'UP', _('UnitProcess')    
    PERSON_PROCESS = 'PP', _('PersonProcess')    
    YR_CLOSE = 'CL', _('YearRoundClose')

# ขั้นตอนของเอกสาร
class HomeRequestProcessStep(models.TextChoices):
    REQUESTER_PROCESS = 'RP', _('RequesterProcess')
    REQUESTER_SENDED = 'RS', _('RequesterSended')
    UNIT_PROCESS = 'UP', _('UnitProcess')
    UNIT_SENDED = 'US', _('UnitSended')
    PERSON_PROCESS = 'PP', _('PersonProcess')
    PERSON_REPORTED = 'PR', _('PersonReported') # ออกรายงาน
    GET_HOUSE = 'GH', _('GetHouse')
    REQUESTER_CANCEL = 'RC', _('RequesterCancel')
    ROUND_FINISHED = 'RF', _('RoundFinished')

# Zone บ้านพัก
HOMEZONE_CHOICE = [
    (0, 'ไม่ระบุ'),
    (1, 'เขต 1 : ท่าดินแดง'),
    (2, 'เขต 2 : ท่าดินแดง'),
    (3, 'เขต 3 : ท่าดินแดง'),
    (6, 'เขต 6 : รถไฟและสีกัน'),
    (7, 'เขต 7 : ลาดเป็ด'),
    (8, 'เขต 8 : บางซื่อ'),
]

# สถานภาพสมรส
PERSON_STATUS_CHOICE = [
    (1, 'โสด'),
    (2, 'สมรส-อยู่ร่วมกัน'),
    (3, 'สมรส-แยกกันอยู่'),
    (4, 'หย่า'),
    (5, 'ม่าย'), ]

# การศึกษาของผู้พักอาศัยร่วม
EDUCATION_CHOICE =  [
    (0, 'Nursery'),
    (1, 'อนุบาล'),
    (2, 'ประถมต้น'),
    (3, 'ประถมปลาย'),
    (4, 'มัธยมต้น'),
    (5, 'มัธยมปลาย'),
    (6, 'อุดมศึกษา'),
    (7, 'บัณฑิตศึกษา'),
    (8, 'ปวช.หรือเทียบเท่า'), 
    (9, 'ปวส.หรือเทียบเท่า'), 
    (10, 'อนุปริญญาหรือเทียบเท่า'), ]

# ผู้ประเมินความเดือดร้อน
FillFormTypeChoice = [
    ('Self', 'ประเมินตนเอง'),
    ('Unit', 'นขต.ประเมิน'),
    ('HR', 'กพ.ทอ.ประเมิน')]