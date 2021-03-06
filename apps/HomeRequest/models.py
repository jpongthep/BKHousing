from datetime import date, timedelta

from django.db import models
from django.db.models.deletion import SET_NULL
from django.urls import reverse
from django.db.models import Q

from apps.Utility.UploadData import UploadFolderName, only_pdf
from apps.Utility.Constants import ( PERSON_STATUS,
                                     EDUCATION, 
                                     CHOICE_Rank,
                                     YEARROUND_PROCESSSTEP,
                                     HomeZone,
                                     CommuteType,
                                     SPOUSEOFFICE,
                                     HomeRequestProcessStep,
                                     CoResidenceRelation,
                                     HomeRentPermission,
                                     HomeRequestType)
from apps.Command.models import Command
from apps.Configurations.models import YearRound
from apps.Home.models import HomeOwner, HomeData
from apps.UserData.models import User, Unit as TheUnit


class CurrentYearManager(models.Manager):
    def get_queryset(self):
        CurrentYearRound = YearRound.objects.filter(CurrentStep__in = ['RS','UP','PP'])[0]
        return super().get_queryset().filter(year_round = CurrentYearRound)


class HomeRequest(models.Model):
    class Meta:
        verbose_name_plural = "HomeRequest : คำร้องขอมีบ้านพัก"

    current_year = CurrentYearManager()
    objects = models.Manager() # The default manager.

    Requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Requester')
    year_round = models.ForeignKey(YearRound, on_delete=models.SET_NULL, null = True, related_name='YearRound')

    # ข้อมูลพื้นฐานส่วนตัว ณ ช่วงเวลาที่ขอ
    Rank = models.PositiveIntegerField(choices = CHOICE_Rank, default = 0, null=True, blank = True)
    FullName = models.CharField(max_length = 255, verbose_name="ยศ - ชื่อ - นามสกุล", null = False, default = '')
    Position = models.CharField(max_length = 200, null=True, verbose_name="ตำแหน่ง")
    sub_unit =  models.CharField(max_length = 30, verbose_name="สังกัดย่อย", null = True, blank=True)
    Unit = models.ForeignKey(TheUnit, models.SET_NULL, null = True, verbose_name="สังกัด", related_name='Unit')

    Salary = models.IntegerField(verbose_name="เงินเดือน(ปัจจุบัน)", null=True, blank=True)
    AddSalary = models.IntegerField(verbose_name="เงินเพิ่ม", null=True, blank=True, default = 0)

    # ที่อยู่ปัจจุบัน
    Address = models.CharField(max_length = 100, null=True, blank=True, verbose_name="ที่อยู่")
    GooglePlusCodes1 = models.CharField(max_length = 60, null=True, blank=True, verbose_name="Google Plus Codes 1")
    distance = models.IntegerField(verbose_name="ระยะทางถึงที่ทำงาน (กม.)", null=True, blank=True, default = 0)
    work_commute =  models.CharField(verbose_name="การเดินทางไปทำงาน", max_length = 5, choices = CommuteType.choices,default = CommuteType.PrivateVehical, null=True, blank = True)
    TravelDescription = models.TextField(null=True, blank=True, verbose_name="บรรยายการเดินทางแต่ละวัน")

    # การเบิกค่าเช่าบ้าน
    RentPermission = models.IntegerField(verbose_name="สิทธิ์เบิกค่าเช่าบ้าน", choices = HomeRentPermission.choices, default = 3)
    have_rent = models.BooleanField(verbose_name = 'มีข้อมูลเบิก (6 เดือน)', default = False)
    have_rent_spouse = models.BooleanField(verbose_name = 'คู่สมรสเบิก (6 เดือน)', default = False)
    RentalCost = models.IntegerField(verbose_name = "ค่าเช่าบ้าน", null=True, blank=True)
    RentalCostSpouse = models.IntegerField(verbose_name = "ค่าเช่าบ้านคู่สมรส", null=True, blank=True)
    rent_comment = models.TextField(verbose_name = "ข้อมูลเพิ่มเติมเกี่ยวกับการเบิก คชบ.", null=True, blank=True)

    # คู่สมรส
    Status = models.IntegerField(verbose_name="สถานภาพ (ยึดตามข้อมูล กพ.ทอ.)", default = PERSON_STATUS.SINGLE, choices=PERSON_STATUS.choices, null=True, blank=True)
    SpouseName = models.CharField(max_length=100, null=True, blank=True, verbose_name="ชื่อคู่สมรส")
    SpousePID = models.CharField(max_length=13, null=True, blank=True, verbose_name="เลขประชาชนคู่สมรส")
    SpouseAFID = models.CharField(max_length=12, null=True, blank=True, verbose_name="เลขประจำตัว ทอ. (ถ้าเป็น)")
    spouse_office = models.IntegerField(verbose_name="สถานที่ทำงานคู่สมรส", choices = SPOUSEOFFICE.choices, default = 0, null = True, blank = True)
    IsHRISReport = models.BooleanField(default = False, verbose_name = 'รายงานคู่สมรสและบุตรในประวัติราชการ')
    num_children = models.IntegerField(verbose_name="จำนวนบุตร", default = 0, null=True, blank=True)
    num_study_children = models.IntegerField(verbose_name="จน.บุตรที่อยู่ระหว่างศึกษา", default = 0, null=True, blank=True)

    # ยืนยันข้อมูล
    IsNotBuyHome = models.BooleanField(default = False, verbose_name = 'ไม่เป็นผู้เบิกค่าเช่าซื้อ')
    IsNotOwnHome = models.BooleanField(default = False, verbose_name = 'ไม่มีกรรมสิทธิ์บ้านรัศมี 20 กม.')
    IsNotRTAFHome = models.BooleanField(default = False, verbose_name = 'คู่สมรสไม่เป็นเจ้าของบ้านพัก ทอ.')
    IsNeverRTAFHome = models.BooleanField(default = False, verbose_name = 'ไม่เคยเป็นเจ้าของบ้านพัก ทอ.')
    RTAFHomeLeaveReason = models.TextField(null=True, blank=True, verbose_name = "ข้อมูลบ้านหลังเดิม และสาเหตุการออก/ถูกไล่ออกจากบ้านพัก (ถ้าเคย)")
    
    # ความเดือดร้อนเบื้องต้น
    IsHomelessDisaster = models.BooleanField(default = False, verbose_name = 'เป็นผู้ไร้บ้านจากอุบัติภัยธรรมชาติ')
    IsHomelessEvict = models.BooleanField(default = False, verbose_name = 'เป็นผู้ไร้บ้านจากการโดนไล่ที่')    
    ContinueHouse = models.BooleanField(default = False, verbose_name = 'ขอเข้าพักอาศัยต่อจากบุพการีหรือคู่สมรส')    
    IsMoveFromOtherUnit = models.BooleanField(default = False, verbose_name = 'เป็นผู้โยกย้ายจากหน่วยที่ตั้งต่างจังหวัดหรือต่างประเทศ')
    ImportanceDuty = models.BooleanField(default = False, verbose_name = 'เป็นผู้ปฏิบัติหน้าที่ราชการสำคัญ')
    OtherTrouble  = models.TextField(null=True, blank=True, verbose_name='เป็นผู้มีความจำเป็นและเดือดร้อนอื่น ๆ ')

    # ความต้องการบ้านประเภทต่าง ๆ 
    IsHomeNeed = models.BooleanField(default = False, verbose_name = 'ต้องการบ้านพัก')
    IsFlatNeed = models.BooleanField(default = False, verbose_name = 'ต้องการแฟลต')
    IsShopHouseNeed = models.BooleanField(default = False, verbose_name = 'ต้องการห้องแถว')

    # ลำดับความต้องการบ้านเขตต่าง ๆ 
    ZoneRequestPriority1 = models.CharField(verbose_name = "ลำดับ 1", choices = HomeZone.choices, max_length= 2, null=True, blank = True)
    ZoneRequestPriority2 = models.CharField(verbose_name = "ลำดับ 2", choices = HomeZone.choices, max_length= 2, null=True, blank = True)
    ZoneRequestPriority3 = models.CharField(verbose_name = "ลำดับ 3", choices = HomeZone.choices, max_length= 2, null=True, blank = True)
    ZoneRequestPriority4 = models.CharField(verbose_name = "ลำดับ 4", choices = HomeZone.choices, max_length= 2, null=True, blank = True)
    ZoneRequestPriority5 = models.CharField(verbose_name = "ลำดับ 5", choices = HomeZone.choices, max_length= 2, null=True, blank = True)
    ZoneRequestPriority6 = models.CharField(verbose_name = "ลำดับ 6", choices = HomeZone.choices, max_length= 2, null=True, blank = True)

    #เอกสารหลักฐาน    
    HouseRegistration = models.FileField(verbose_name='สำเนาทะเบียนบ้าน', default = None, null = True, blank = True, upload_to = UploadFolderName, validators = [only_pdf])
    MarriageRegistration = models.FileField(verbose_name='ทะเบียนสมรส', default = None, null = True, blank = True, upload_to = UploadFolderName, validators = [only_pdf])
    SpouseApproved = models.FileField(verbose_name='หนังสือรับรองของคู่สมรส (ถ้ามี)', default = None, null = True, blank = True, upload_to = UploadFolderName, validators = [only_pdf])
    DivorceRegistration = models.FileField(verbose_name='ทะเบียนหย่า (ถ้ามี)', default = None, null = True, blank = True, upload_to = UploadFolderName, validators = [only_pdf])
    SpouseDeathRegistration = models.FileField(verbose_name='มรณบัตรคู่สมรส (ถ้ามี)', default = None, null = True, blank = True, upload_to = UploadFolderName, validators = [only_pdf])
    more_evidence = models.FileField(verbose_name='เอกสารเพิ่มเติม', default = None, null = True, blank = True, upload_to = UploadFolderName, validators = [only_pdf])

    Comment = models.TextField(verbose_name="หมายเหตุ", null=True, blank = True)

    ProcessStep = models.CharField(verbose_name="ขั้นตอนเอกสาร", max_length = 2, choices = HomeRequestProcessStep.choices,default = HomeRequestProcessStep.REQUESTER_PROCESS)
    cancel_request = models.BooleanField(verbose_name = 'ผู้ส่งขอยกเลิกคำขอ', default = False)
    # วันที่ส่งเอกสารของผู้ขอบ้าน
     
    RequesterDateSend = models.DateField(verbose_name = 'วันที่ขรก.ส่งเอกสาร',default = None,null = True, blank = True)
    request_type =  models.CharField(verbose_name="ประเภทคำขอ", max_length = 2, choices = HomeRequestType.choices,default = HomeRequestType.NEW, null=True, blank = True)

    # ผู้รับส่งและวันที่รับส่งเอกสารของ นขต.
    UnitReciever = models.ForeignKey(User, verbose_name = "ผู้รับเอกสาร(นขต.)", null = True, blank = True, default = None, on_delete=models.SET_NULL, related_name='UnitReciever')
    UnitDateRecieved = models.DateField(verbose_name = "วันที่หน่วยรับเอกสาร(นขต.)", default=None, null=True, blank=True)
    UnitApprover = models.ForeignKey(User, verbose_name = "ผู้ส่งเอกสาร(นขต.)", null = True, blank = True, default = None, on_delete=models.SET_NULL, related_name='UnitApprover')
    UnitDateApproved = models.DateField(verbose_name = "วันที่หน่วยส่งเอกสาร", default=None, null=True, blank=True)    

    # ผู้รับส่งและวันที่รับส่งเอกสารของ กพ.ทอ.
    PersonReciever = models.ForeignKey(User, verbose_name = "ผู้รับเอกสาร(กพ.ทอ.)", null = True, blank = True, default = None, on_delete=models.SET_NULL, related_name='PersonReciever')
    PersonDateRecieved = models.DateField(verbose_name = "วันที่หน่วยรับเอกสาร(กพ.ทอ.)", default=None, null=True, blank=True)
    PersonApprover = models.ForeignKey(User, verbose_name = "ผู้ส่งเอกสาร(กพ.ทอ.)", null = True, blank = True, default = None, on_delete=models.SET_NULL, related_name='PersonApprover')
    PersonDateApproved = models.DateField(verbose_name = "วันที่กำลังพลรับเอกสาร", default=None, null=True, blank=True)

    # แบบประเมินความเดือดร้อน 2 ส่วน หน่วยงาน และ กพ.ทอ.
    IsUnitEval = models.BooleanField(verbose_name = 'นขต.ประเมินเรียบร้อย', default = False)
    UnitTroubleScore = models.IntegerField(verbose_name="คะแนนประเมิน นขต.", null=True,blank = True)
    IsPersonEval =  models.BooleanField(verbose_name = 'กพ.ทอ.ประเมินเรียบร้อย', default = False)
    PersonTroubleScore = models.IntegerField(verbose_name="คะแนนประเมิน กพ.", null=True,blank = True)
    #คะแนนประเมินล่าสุด
    TroubleScore = models.IntegerField(verbose_name="คะแนนประเมินล่าสุด", null=True,blank = True)

    home_allocate = models.ForeignKey(HomeData, verbose_name = "บ้านที่ได้รับจัดสรร", null = True, blank = True, default = None, on_delete=models.SET_NULL, related_name='home_allocate')
    enter_command = models.ForeignKey(Command,verbose_name='คำสั่งเข้าพัก', on_delete=models.SET_NULL, related_name= "new_hr_enter_command", default = None,null = True, blank = True)
    lastest_allocate =  models.BooleanField(verbose_name = 'จัดสรรล่าสุด', default = False)
    published =  models.BooleanField(verbose_name = 'ประกาศคำสั่งแล้ว', default = False)
    moved_data =  models.BooleanField(verbose_name = 'ย้ายข้อมูลเข้าบ้านพักแล้ว', default = False)
    make_contract = models.BooleanField(verbose_name = 'ทำสัญญาแล้วเข้าบ้านพักแล้ว', default = False)

    recorder = models.ForeignKey(User, on_delete = models.DO_NOTHING, related_name='recorder_admin',default = None, null=True,blank = True)
    specificed_need = models.CharField(verbose_name="ความต้องการเฉพาะเจาะจง", max_length = 50, default = '', null=True,blank = True)
    foster_person = models.CharField(verbose_name="ผู้ฝาก", max_length = 50, default = '', null=True,blank = True)
    foster_date = models.DateField(verbose_name = "วันที่รับฝาก", default=date.today, null=True, blank=True)
    foster_reason = models.CharField(verbose_name="หมายเหตุผู้ฝาก", max_length = 100, default = '', null=True,blank = True)
    have_document = models.BooleanField(verbose_name = 'มีเอกสารคำขอ', default = True)
    document_number = models.CharField(verbose_name="เลข กห.", default = '', max_length = 200, null=True,blank = True)
    document_date = models.DateField(verbose_name="ลงวันที่", default = date.today, max_length = 200, null=True,blank = True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    OriginProcessStep = None

    def update_process_step(self, ProcessStep, user):

        if ProcessStep != self.OriginProcessStep:
            if ProcessStep == HomeRequestProcessStep.REQUESTER_SENDED:
                self.RequesterDateSend = date.today()

            if ProcessStep == HomeRequestProcessStep.UNIT_PROCESS:
                self.UnitReciever = user
                self.UnitDateRecieved = date.today()

            if ProcessStep == HomeRequestProcessStep.UNIT_SENDED:
                self.UnitApprover = user
                self.UnitDateApproved = date.today()

            if ProcessStep == HomeRequestProcessStep.PERSON_PROCESS:
                self.PersonReciever = user
                self.PersonDateRecieved = date.today()

            if ProcessStep == HomeRequestProcessStep.PERSON_ACCEPTED:
                self.PersonApprover = user
                self.PersonDateApproved = date.today()

            self.OriginProcessStep = ProcessStep
            self.ProcessStep = ProcessStep
            print('HR save data :',ProcessStep, user )
            self.save()


    def __init__(self, *args, **kwargs):
        super(HomeRequest, self).__init__(*args, **kwargs)
        self.OriginProcessStep = self.ProcessStep

    # def clean(self):
    #     from django.core.exceptions import ValidationError
    #     print("model clean")
    #     if self.RequesterDateSend:
    #         if not self.ZoneRequestPriority1:
    #             raise ValidationError('กรุณากรอกลำดับความต้องการ')
        

    def get_absolute_url(self):
        return reverse('HomeRequest:af_person')

    @property
    def RequesterSended(self):
        return self.RequesterDateSend

    @property
    def WorkYear(self):
        today = date.today()
        return today.year - self.PlacementDate.year

    @property
    def still_active(self):
        return self.ProcessStep not in ['RC','RF','GH']
    
    def process_value(self):
        step = ['RP','RS','UP','US','PP','PA','GH']
        if self.ProcessStep in step:
            return step.index(self.ProcessStep)
        elif self.ProcessStep in ['RC','RF']:
            return 0
    
    def PriorityList(self):
        text = ""
        priority_list = [self.ZoneRequestPriority1,self.ZoneRequestPriority2,self.ZoneRequestPriority3,self.ZoneRequestPriority4,self.ZoneRequestPriority5,self.ZoneRequestPriority6]
        priority_list = [x for x in priority_list if x]
        return ">".join(priority_list)


    def status_icon(self):
        if self.Status == 'โสด':
            return 'my_images/together.jpg'

    def __str__(self):
        return f'{self.year_round} : {self.Requester.FullName}'


# ผู้ที่พักอาศัยอยู่ร่วมกัน
class CoResident(models.Model):
    home_request = models.ForeignKey(HomeRequest, on_delete=models.CASCADE, related_name='CoResident')
    PersonID = models.CharField(verbose_name="เลขประจำตัวประชาชน", max_length = 13)
    FullName = models.CharField(verbose_name="ยศ - ชื่อ - นามสกุล", max_length = 150, null = False, blank = False, default = '')
    BirthDay = models.DateField(verbose_name="วันเกิด", null = True, blank = True)
    Relation = models.CharField(verbose_name="ความสัมพันธ์", max_length = 4, choices = CoResidenceRelation.choices)
    Occupation = models.CharField(verbose_name="อาชีพ", max_length = 20, null = True, blank = True)
    Salary = models.IntegerField(verbose_name="รายได้", null = True, blank = True, default = 0)
    IsAirforce = models.BooleanField(verbose_name = "เป็น ขรก.ทอ.", default = False)
    Education = models.IntegerField(verbose_name="การศึกษา", choices=EDUCATION.choices, null = True, blank = True)

    def Age(self):
        if not self.BirthDay:
            return "-"
        else:
            today = date.today()
            return today.year - self.BirthDay.year

    def __str__(self):
        return self.FullName

    def get_absolute_url(self):
        hrid = self.home_request.id
        return reverse('HomeRequest:detail', kwargs={"pk": hrid})      


class HomeChange(models.Model):
    class Meta:
        verbose_name_plural = "HomeChange : คำร้องขอเปลี่ยน/สับเปลี่ยนบ้านพัก"

    Requester = models.ForeignKey(User,verbose_name="ผู้ขอ", on_delete=models.CASCADE, related_name='home_change_requester')
    request_type =  models.CharField(verbose_name="ประเภทคำขอ", max_length = 2, choices = HomeRequestType.choices,default = HomeRequestType.CHANGE , null=True, blank = True)
    current_home_owner = models.ForeignKey(HomeOwner,verbose_name="เจ้าของบ้านพัก", on_delete=models.CASCADE, related_name='current_home_owner')
    year_round = models.ForeignKey(YearRound, on_delete=models.SET_NULL, null = True, related_name='home_change_YearRound')


    # ข้อมูลพื้นฐานส่วนตัว ณ ช่วงเวลาที่ขอ
    Rank = models.PositiveIntegerField(choices = CHOICE_Rank, default = 0, null=True, blank = True)
    FullName = models.CharField(max_length = 255, verbose_name="ยศ - ชื่อ - นามสกุล", null = False, default = '')
    Position = models.CharField(max_length = 200, null=True, verbose_name="ตำแหน่ง")
    sub_unit =  models.CharField(max_length = 30, verbose_name="สังกัดย่อย", null = True, blank=True)
    Unit = models.ForeignKey(TheUnit, on_delete= models.SET_NULL, null = True, verbose_name="สังกัด", related_name='home_change_Unit')

    Salary = models.IntegerField(verbose_name="เงินเดือน(ปัจจุบัน)", null=True, blank=True)
    AddSalary = models.IntegerField(verbose_name="เงินเพิ่ม", null=True, blank=True, default = 0)

    # คู่สมรส
    Status = models.IntegerField(verbose_name="สถานภาพ (ยึดตามข้อมูล กพ.ทอ.)", default = PERSON_STATUS.SINGLE, choices=PERSON_STATUS.choices, null=True, blank=True)
    SpouseName = models.CharField(max_length = 100, null=True, blank=True, verbose_name="ชื่อคู่สมรส")
    SpousePID = models.CharField(max_length = 13, null=True, blank=True, verbose_name="เลขประชาชนคู่สมรส")
    SpouseAFID = models.CharField(max_length = 12, null=True, blank=True, verbose_name="เลขประจำตัว ทอ. (ถ้าเป็น)")
    spouse_office = models.IntegerField(verbose_name = "สถานที่ทำงานคู่สมรส", choices = SPOUSEOFFICE.choices, default = 0, null = True, blank = True)
    IsHRISReport = models.BooleanField(default = False, verbose_name = 'รายงานคู่สมรสและบุตรในประวัติราชการ')
    num_children = models.IntegerField(verbose_name = "จำนวนบุตร", default = 0, null=True, blank=True)
    num_study_children = models.IntegerField(verbose_name = "จน.บุตรที่อยู่ระหว่างศึกษา", default = 0, null=True, blank=True)
   
    change_comment = models.TextField(verbose_name="สาเหตุของการเปลี่ยน/สับเปลี่ยน", null=True, blank = True)
    new_home = models.ForeignKey(HomeData, verbose_name="บ้านใหม่", on_delete = models.SET_NULL, null = True, related_name='new_home')
    swap_home_owner =  models.ForeignKey(HomeOwner,verbose_name="เจ้าของบ้านพัก (กรณีสลับ)", on_delete=models.SET_NULL, related_name='swap_home_owner', null = True)

    specificed_need = models.CharField(verbose_name="ความต้องการเฉพาะเจาะจง", max_length = 50, default = '', null=True,blank = True)
    # ความต้องการบ้านประเภทต่าง ๆ 
    IsHomeNeed = models.BooleanField(default = False, verbose_name = 'ต้องการบ้านพัก')
    IsFlatNeed = models.BooleanField(default = False, verbose_name = 'ต้องการแฟลต')
    IsShopHouseNeed = models.BooleanField(default = False, verbose_name = 'ต้องการห้องแถว')

    # ลำดับความต้องการบ้านเขตต่าง ๆ 
    ZoneRequestPriority1 = models.CharField(verbose_name = "ลำดับ 1", choices = HomeZone.choices, max_length= 2, null=True, blank = True)
    ZoneRequestPriority2 = models.CharField(verbose_name = "ลำดับ 2", choices = HomeZone.choices, max_length= 2, null=True, blank = True)
    ZoneRequestPriority3 = models.CharField(verbose_name = "ลำดับ 3", choices = HomeZone.choices, max_length= 2, null=True, blank = True)
    ZoneRequestPriority4 = models.CharField(verbose_name = "ลำดับ 4", choices = HomeZone.choices, max_length= 2, null=True, blank = True)
    ZoneRequestPriority5 = models.CharField(verbose_name = "ลำดับ 5", choices = HomeZone.choices, max_length= 2, null=True, blank = True)
    ZoneRequestPriority6 = models.CharField(verbose_name = "ลำดับ 6", choices = HomeZone.choices, max_length= 2, null=True, blank = True)

    Comment = models.TextField(verbose_name="หมายเหตุ", null=True, blank = True)

    ProcessStep = models.CharField(verbose_name="ขั้นตอนเอกสาร", max_length = 2, choices = HomeRequestProcessStep.choices,default = HomeRequestProcessStep.REQUESTER_PROCESS)
    cancel_request = models.BooleanField(verbose_name = 'ผู้ส่งขอยกเลิกคำขอ', default = False)
    # วันที่ส่งเอกสารของผู้ขอบ้าน
     
    RequesterDateSend = models.DateField(verbose_name = 'วันที่ขรก.ส่งเอกสาร',default = None,null = True, blank = True)
    # ผู้รับส่งและวันที่รับส่งเอกสารของ นขต.
    UnitReciever = models.ForeignKey(User, verbose_name = "ผู้รับเอกสาร(นขต.)", null = True, blank = True, default = None, on_delete=models.SET_NULL, related_name='home_change_UnitReciever')
    UnitDateRecieved = models.DateField(verbose_name = "วันที่หน่วยรับเอกสาร(นขต.)", default=None, null=True, blank=True)
    UnitApprover = models.ForeignKey(User, verbose_name = "ผู้ส่งเอกสาร(นขต.)", null = True, blank = True, default = None, on_delete=models.SET_NULL, related_name='home_change_UnitApprover')
    UnitDateApproved = models.DateField(verbose_name = "วันที่หน่วยส่งเอกสาร", default=None, null=True, blank=True)    

    # ผู้รับส่งและวันที่รับส่งเอกสารของ กพ.ทอ.
    PersonReciever = models.ForeignKey(User, verbose_name = "ผู้รับเอกสาร(กพ.ทอ.)", null = True, blank = True, default = None, on_delete=models.SET_NULL, related_name='home_change_PersonReciever')
    PersonDateRecieved = models.DateField(verbose_name = "วันที่หน่วยรับเอกสาร(กพ.ทอ.)", default=None, null=True, blank=True)
    PersonApprover = models.ForeignKey(User, verbose_name = "ผู้ส่งเอกสาร(กพ.ทอ.)", null = True, blank = True, default = None, on_delete=models.SET_NULL, related_name='home_change_PersonApprover')
    PersonDateApproved = models.DateField(verbose_name = "วันที่กำลังพลรับเอกสาร", default=None, null=True, blank=True)

    # # แบบประเมินความเดือดร้อน 2 ส่วน หน่วยงาน และ กพ.ทอ.
    # IsUnitEval = models.BooleanField(verbose_name = 'นขต.ประเมินเรียบร้อย', default = False)
    # UnitTroubleScore = models.IntegerField(verbose_name="คะแนนประเมิน นขต.", null=True,blank = True)
    # IsPersonEval =  models.BooleanField(verbose_name = 'กพ.ทอ.ประเมินเรียบร้อย', default = False)
    # PersonTroubleScore = models.IntegerField(verbose_name="คะแนนประเมิน กพ.", null=True,blank = True)
    # #คะแนนประเมินล่าสุด
    # TroubleScore = models.IntegerField(verbose_name="คะแนนประเมินล่าสุด", null=True,blank = True)

    recorder = models.ForeignKey(User, verbose_name="ผู้บันทึก", on_delete = models.DO_NOTHING, related_name='home_change_recorder_admin',default = None, null=True,blank = True)
    foster_person = models.CharField(verbose_name="ผู้ฝาก", max_length = 50, default = '', null=True,blank = True)
    foster_date = models.DateField(verbose_name = "วันที่รับฝาก", default=date.today, null=True, blank=True)
    foster_reason = models.CharField(verbose_name="หมายเหตุผู้ฝาก", max_length = 100, default = '', null=True,blank = True)
    have_document = models.BooleanField(verbose_name = 'มีเอกสารคำขอ', default = True)
    document_number = models.CharField(verbose_name="เลข กห.", default = '', max_length = 200, null=True,blank = True)
    document_date = models.DateField(verbose_name="ลงวันที่", default = date.today, max_length = 200, null=True,blank = True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
