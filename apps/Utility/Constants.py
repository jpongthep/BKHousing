from django.db import models
from django.utils.translation import gettext_lazy as _

USER_PERMISSION = (
    ("RTAF_NO_HOME_USER", "RTAF_no_home_user"),
    ("RTAF_HOME_USER", "RTAF_home_user"),
    ("PERSON_UNIT_ADMIN", "Person_unit_admin"),
    ("PERSON_ADMIN", "Person_admin"),
    ("HOME_EXAMINE_OFFICER", "Home_examine_officer"),
    ("MP_OFFICER", "MP_officer"),
    ("FINANCIAL_OFFICER", "Financial_officer"),
    ("CIVIL_OFFICER", "Civil_officer"),
)


class RTAFUnitSection(models.TextChoices):    
    NotDefine = '0', _('-')
    Commander = '1', _('ส่วนบังคับบัญชา')
    AFHeadquater = '2', _('กองทัพอากาศ (กองบัญชาการ)')
    Headquater = '3', _('ส่วนบัญชาการ')
    Fighter = '4', _('ส่วนกำลังรบ')
    Support = '5', _('ส่วนส่งกำลังบำรุง')
    Education = '6', _('ส่วนการศึกษา')
    Special = '7', _('ส่วนกิจการพิเศษ')

CHOICE_Rank = (
    ( 30101 ,  'พล.อ.อ.*' ) ,
    ( 30102 ,  'พล.อ.อ.*หญิง' ) ,
    ( 30211 ,  'พล.อ.อ.' ) ,
    ( 30212 ,  'พล.อ.อ.หญิง' ) ,
    ( 30213 ,  'พล.อ.' ) ,
    ( 30221 ,  'พล.อ.ท.' ) ,
    ( 30222 ,  'พล.อ.ท.หญิง' ) ,
    ( 30231 ,  'พล.อ.ต.' ) ,
    ( 30232 ,  'พล.อ.ต.หญิง' ) ,
    ( 30301 ,  'น.อ.(พ)' ) ,
    ( 30302 ,  'น.อ.(พ) หญิง' ) ,
    ( 30410 ,  'พ.อ.' ) ,
    ( 30411 ,  'น.อ.' ) ,
    ( 30412 ,  'น.อ.หญิง' ) ,
    ( 30420 ,  'พ.ท.' ) ,
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
    ( 30831 ,  'จ.ต.' ) ,
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
    ( 40600 ,  'นาย' ) ,
    ( 40601 ,  'นาง' ) ,
    ( 40602 ,  'น.ส.' ) ,
    ( 0 ,  '' )
) 

# HomeDataType,

# 1234
#1 H = บ้าน  F = แฟลต R = เรือนแถว
#2 G = นายพล O = สัญญาบัตร N = ประทวน
#34 5 = น.5 F = ครอบครัว SF = โสดหญิง  SM = โสดชาย
class HomeDataType(models.TextChoices):
    NA = '-', _('ไม่ระบุ')
    HG = 'HG', _('นายพล')
    HO5 = 'HO5', _('น.5 หลัง (เรือนแถว)')
    HOF = 'HOF', _('น.บ้านเดี่ยว')    
    RNF = 'RNF', _('เรือนแถวประทวน')    
    FNF = 'FNF', _('แฟลตประทวน')
    FNSF = 'FNSF', _('แฟลตประทวน (โสด ญ.)')
    FNSM = 'FNSM', _('แฟลตประทวน (โสด)')
    FOF = 'FOF', _('แฟลตสัญญาบัตร')
    FOSF = 'FOSF', _('แฟลตสัญญาบัตร(โสด ญ.)')
    FOSM = 'FOSM', _('แฟลตสัญญาบัตร(โสด)')
    RF = 'RF', _('เรือนแถวสัญญาบัตร')
    FMIX = 'FM', _('แฟลตผสม')
    
class HomeZone(models.TextChoices):
    Z1 = '1', _('เขต 1 : ท่าดินแดง')
    Z2 = '2', _('เขต 2 : ท่าดินแดง')
    Z3 = '3', _('เขต 3 : ท่าดินแดง')
    Z6Train = '6T', _('เขต 6 : รถไฟ')
    Z6Sekan = '6S', _('เขต 6 : สีกัน')
    Z7 = '7S', _('เขต 7 : ลาดเป็ด')
    ZBangsue = 'BS', _('บางซื่อ')

class HomeDataStatus(models.TextChoices):
    STAY = 'ST', _('พักอาศัย')
    WAIT = 'WT', _('รอจัดสรร')
    WAITCHECK = 'WC', _('รอตรวจสอบ')
    WAITFIX = 'WF', _('รอซ่อม')
    FIX = 'FX', _('ซ่อม')
    REMOVE = 'RM', _('รื้อถอน')

class PAYMENT_METHOD(models.IntegerChoices):
    NOMETHOD = 0, _('ไม่ระบุ')
    CASH = 1, _('จ่ายเงินสด')
    ACCOUNT = 2, _('หักบัญชี')

class HomeDataGrade(models.TextChoices):    
    NO = '?', _('?')
    A = 'A', _('A')
    A_Minus = 'A-', _('A-')
    B_Plus = 'B+', _('B+')
    B = 'B', _('B')
    B_Minus = 'B-', _('B-')
    C = 'C', _('C')
    
class OwnerLeaveType(models.TextChoices):
    STAY = '-', _('-')
    RetiredAF = 'RA', _('เกษียณ - ใน ทอ.')
    WAITCHECK = 'WC', _('รอตรวจสอบ')
    WAITFIX = 'WF', _('รอซ่อม')
    FIX = 'FX', _('ซ่อม')

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
    PERSON_ACCEPTED = 'PA', _('PersonAccepted') # ออกรายงาน
    GET_HOUSE = 'GH', _('GetHouse')
    REQUESTER_CANCEL = 'RC', _('RequesterCancel')
    ROUND_FINISHED = 'RF', _('RoundFinished')


# ขั้นตอนของเอกสาร
class CoResidenceRelation(models.TextChoices):
    SPOUSE = '1-SP', _('คู่สมรส')    
    CHILD = '2-CH', _('บุตร')
    FATHER = '3-FA', _('บิดา')
    MOTHER = '4-MO', _('มารดา')
    BROSIS = '5-BS', _('พี่น้อง')
    RELATIVE = '6-RE', _('ญาติ') 
    INHABITANT = '7-IH', _('ผู้อาศัย')    

class PERSON_STATUS(models.IntegerChoices):
    NOSTATUS = 0, _('-')
    SINGLE = 1, _('โสด')
    MARRIES_TOGETHER = 2, _('สมรส-อยู่ร่วมกัน')
    MARRIES_SEPARATE = 7, _('สมรส-แยกกันอยู่')
    DIVOTE = 3, _('หย่าร้าง')
    WIDOW = 4, _('ม่าย')
    
# การศึกษาของผู้พักอาศัยร่วม
class EDUCATION(models.IntegerChoices):
    Nursery = 0, _('Nursery')
    KindleGarden = 1, _('อนุบาล')
    JuniorElementary = 2, _('ประถมต้น')
    SeniorElementary = 3, _('ประถมปลาย')
    JuniorHighSchool = 4, _('มัธยมต้น')
    SeniorHighSchool = 5, _('มัธยมปลาย')
    Bachelor = 6, _('อุดมศึกษา')
    Graduate = 7, _('บัณฑิตศึกษา')
    Vocational = 8, _('ปวช.หรือเทียบเท่า'),
    HighVocational  = 9, _('ปวส.หรือเทียบเท่า'),
    MiniBachelor = 10, _('อนุปริญญาหรือเทียบเท่า'), 

# การศึกษาของผู้พักอาศัยร่วม
class HomeRentPermission(models.IntegerChoices):
    no_permission = 1, _('ไม่มีสิทธิ์เบิกค่าเช่าบ้าน')
    not_use = 2, _('มีสิทธิ์แต่ไม่ได้เบิกค่าเช่าบ้าน')
    used = 3, _('มีและใช้สิทธิ์เบิกค่าเช่าบ้าน')

# ผู้ประเมินความเดือดร้อน
FillFormTypeChoice = [
    ('Self', 'ประเมินตนเอง'),
    ('Unit', 'นขต.ประเมิน'),
    ('HR', 'กพ.ทอ.ประเมิน')]