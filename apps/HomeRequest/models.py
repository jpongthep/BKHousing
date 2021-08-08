from datetime import date

from django.db import models
from django.urls import reverse

from apps.Utility.UploadData import UploadFolderName
from apps.Utility.Constants import ( PERSON_STATUS_CHOICE, 
                                     EDUCATION_CHOICE, 
                                     CHOICE_Rank,
                                     HOMEZONE_CHOICE)

from apps.Configurations.models import YearRound
from apps.UserData.models import User, Unit as TheUnit


class HomeRequest(models.Model):
    class Meta:
        verbose_name_plural = "HomeRequest : คำร้องขอมีบ้านพัก"
        ordering = ["id"]  

    Requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Requester')
    DateSend = models.DateField(default = date.today())
    YearRound = models.ForeignKey(YearRound, on_delete=models.SET_NULL, null = True, related_name='Requester')

    # ข้อมูลพื้นฐานส่วนตัว ณ ช่วงเวลาที่ขอ
    Rank = models.PositiveIntegerField(choices = CHOICE_Rank, default = 0, null=True)
    FullName = models.CharField(max_length = 255, verbose_name="ยศ - ชื่อ - นามสกุล", null = False, default = '')
    Position = models.CharField(max_length = 200, null=True, verbose_name="ตำแหน่ง")
    Unit = models.ForeignKey(TheUnit, models.SET_NULL, null = True, verbose_name="สังกัด", related_name='Unit')

    Salary = models.IntegerField(verbose_name="เงินเดือน(ปัจจุบัน)")
    AddSalary = models.IntegerField(verbose_name="เงินเพิ่ม")

    # การบรรจุครั้งแรก
    PlacementUnit = models.ForeignKey(TheUnit, models.SET_NULL, null = True, verbose_name="สังกัดบรรจุ", related_name='PlacementUnit')
    command_of_placement = models.CharField(max_length = 100, null = True,verbose_name="ที่คำสั่งบรรจุ")
    PlacementCommandDate = models.DateField(null = True,verbose_name="ลงวันที่")
    PlacementDate = models.DateField(null = True,verbose_name="เริ่มบรรจุเมื่อ")

    # ที่อยู่ปัจจุบัน
    Address = models.CharField(max_length = 100, verbose_name="ที่อยู่")
    SubDistinct = models.CharField(max_length = 50, null=True, verbose_name="ตำบล")
    Distinct = models.CharField(max_length = 50, null=True, verbose_name="อำเภอ")    
    Province = models.CharField(max_length = 50, null=True, verbose_name="จังหวัด")
    GooglePlusCodes1 = models.CharField(max_length = 20, null=True, verbose_name="Google Plus Codes 1")
    TravelDescription = models.TextField(null=True, verbose_name="บรรยายการเดินทางแต่ละวัน")

    # การเบิกค่าเช่าบ้าน
    RentPermission = models.BooleanField(default = False, verbose_name="มีสิทธิ์เบิกค่าเช่าบ้าน")
    IsHomeRent = models.BooleanField(default = False, verbose_name="เบิกค่าเช่าบ้านอยู่ก่อน")

    RentAddress = models.CharField(max_length = 100, verbose_name="ที่อยู่")
    RentSubDistinct = models.CharField(max_length = 50, null=True, verbose_name="ตำบล")
    RentDistinct = models.CharField(max_length = 50, null=True, verbose_name="อำเภอ")    
    RentProvince = models.CharField(max_length = 50, null=True, verbose_name="จังหวัด")
    GooglePlusCodes2 = models.CharField(max_length = 20, null=True, verbose_name="Google Plus Codes 2")

    RentStartDate = models.DateField(verbose_name = "วันเริ่มสัญญาเช่าบ้าน", default=None, null=True, blank=True)
    RentEndDate = models.DateField(verbose_name = "วันสิ้นสุดสัญญาเช่าบ้าน", default=None, null=True, blank=True)
    RentOwner = models.CharField(max_length = 255, verbose_name = "ชื่อผู้ให้เช่า", null=True, blank=True)
    RentOwnerPID = models.CharField(max_length = 13, verbose_name = "PID ผู้ให้เช่า", null=True, blank=True)
    RentalCost = models.IntegerField(verbose_name = "ค่าเช่าบ้าน", null=True, blank=True)

    # คู่สมรส
    Status = models.IntegerField(choices=PERSON_STATUS_CHOICE, verbose_name="สถานภาพ")
    SpouseName = models.CharField(max_length=100, null=True, blank=True, verbose_name="ชื่อคู่สมรส")
    SpousePID = models.CharField(max_length=13, null=True, blank=True, verbose_name="PID คู่สมรส")
    SpouseAFID = models.CharField(max_length=12, null=True, blank=True, verbose_name="เลขประจำตัว ทอ.")
    IsHRISReport = models.BooleanField(default = False, verbose_name = 'รายงานภรรยาและบุตรในประวัติราชการ')

    # ยืนยันข้อมูล
    IsNotBuyHome = models.BooleanField(default = False, verbose_name = 'ไม่เป็นผู้เบิกค่าเช่าซื้อ')
    IsNotOwnHome = models.BooleanField(default = False, verbose_name = 'ไม่มีกรรมสิทธิ์บ้านรัศมี 20 กม.')
    IsNotRTAFHome = models.BooleanField(default = False, verbose_name = 'ไม่เป็นเจ้าของบ้านพัก ทอ.')
    IsNeverRTAFHome = models.BooleanField(default = False, verbose_name = 'ไม่เคยเป็นเจ้าของบ้านพัก ทอ.')
    RTAFHomeLeaveReason = models.CharField(max_length = 150, null=True, blank=True, verbose_name = "สาเหตุการออกจากบ้านพักครั้งก่อน")
    RTAFHomeFireReason = models.CharField(max_length = 150, null=True, blank=True, verbose_name = "สาเหตุการถูกไล่ออกจากบ้านพักครั้งก่อน")

    # ความเดือดร้อนเบื้องต้น
    IsHomelessDisaster = models.BooleanField(default = False, verbose_name = 'เป็นผู้ไร้บ้านจากอุบัติภัยธรรมชาติ')
    IsHomelessEvict = models.BooleanField(default = False, verbose_name = 'เป็นผู้ไร้บ้านจากการโดนไล่ที่')
    ExRTAFHome = models.CharField(max_length = 150, null=True, blank=True, verbose_name="ข้อมูลบ้านพัก ทอ. หลังเดิม")
    IsMoveFromOtherUnit = models.BooleanField(default = False, verbose_name = 'เป็นผู้โยกย้ายจากภายนอกพื้นที่')
    ImportanceDuty = models.BooleanField(default = False, verbose_name = 'เป็นผู้ปฏิบัติหน้าที่สำคัญ')
    OtherTrouble  = models.CharField(max_length = 150, null=True, blank=True, verbose_name='เป็นผู้ประสบเหตุเดือดร้อนอื่น ๆ (ระบุ) ')

    # ความต้องการบ้านประเภทต่าง ๆ 
    IsHomeNeed = models.BooleanField(default = False, verbose_name = 'ต้องการบ้านพัก')
    IsFlatNeed = models.BooleanField(default = False, verbose_name = 'ต้องการแฟลต')
    IsShopHouseNeed = models.BooleanField(default = False, verbose_name = 'ต้องการห้องแถว')

    # ลำดับความต้องการบ้านเขตต่าง ๆ 
    ZoneRequestPriority1 = models.IntegerField(choices = HOMEZONE_CHOICE, null=True, blank = True, verbose_name = "ลำดับ 1")
    ZoneRequestPriority2 = models.IntegerField(choices = HOMEZONE_CHOICE, null=True, blank = True, verbose_name = "ลำดับ 2")
    ZoneRequestPriority3 = models.IntegerField(choices = HOMEZONE_CHOICE, null=True, blank = True, verbose_name = "ลำดับ 3")
    ZoneRequestPriority4 = models.IntegerField(choices = HOMEZONE_CHOICE, null=True, blank = True, verbose_name = "ลำดับ 4")
    ZoneRequestPriority5 = models.IntegerField(choices = HOMEZONE_CHOICE, null=True, blank = True, verbose_name = "ลำดับ 5")
    ZoneRequestPriority6 = models.IntegerField(choices = HOMEZONE_CHOICE, null=True, blank = True, verbose_name = "ลำดับ 6")

    #เอกสารหลักฐาน    
    HouseRegistration = models.FileField(default = None, null = True, blank = True, upload_to = UploadFolderName, verbose_name='ทะเบียนบ้าน')
    DivorceRegistration = models.FileField(default = None, null = True, blank = True, upload_to = UploadFolderName, verbose_name='ทะเบียนหย่า (ถ้ามี)')
    SpouseDeathRegistration = models.FileField(default = None, null = True, blank = True, upload_to = UploadFolderName, verbose_name='มรณบัตรคู่สมรส (ถ้ามี)')
    HomeRent6006 = models.FileField(default = None, null = True, blank = True, upload_to = UploadFolderName)
    SpouseHomeRent6006 = models.FileField(default = None, null = True, blank = True, upload_to = UploadFolderName)
    SalaryBill = models.FileField(default = None, null = True, blank = True, upload_to = UploadFolderName, verbose_name='สลิปเงินเดือนล่าสุด')
    SpouseApproved = models.FileField(default = None, null = True, blank = True, upload_to = UploadFolderName, verbose_name='หนังสือรับรองจากคู่สมรส')

    HomeRequestFormStatusChoice = [(1, 'ฉบับร่าง'),
                                   (2, 'เอกสารไม่ครบ'),
                                   (3, 'รอดำเนินการ'),
                                   (4, 'อนุมัติ'),
                                   (5, 'ไม่อนุมัติ'),]

    FormStatus = models.IntegerField(
        choices=HomeRequestFormStatusChoice, 
        default= 1, 
        verbose_name="สถานะของเอกสาร")

    ProcedureStatusChoice = [(1, 'ขรก.กรอกฟอร์มแล้ว'), 
                             (2, 'นขต.รับเรื่องแล้ว'), 
                             (3, 'กพ.ทอ.รับเรื่องแล้ว'), 
                             (4, 'อนุมัติ'), 
                             (5, 'ไม่อนุมัติ'), ]
    ProcedureStatus = models.IntegerField(
        choices=ProcedureStatusChoice, 
        default= 1 , 
        verbose_name="สถานะขอบ้าน")

    Comment = models.TextField(null=True, blank = True, verbose_name="หมายเหตุ")

    UnitApprover = models.ForeignKey(User, null = True, blank = True, default = None, on_delete=models.CASCADE, related_name='UnitApprover')
    PersonApprover = models.ForeignKey(User, null = True, blank = True, default = None, on_delete=models.CASCADE, related_name='PersonApprover')

    # แบบประเมินความเดือดร้อน 3 ส่วน ตนเอง หน่วยงาน และ กพ.ทอ.
    IsTroubleSelf = models.BooleanField(default = False, verbose_name = 'ให้คะแนนประเมินตนเองเรียบร้อย')
    IsTroubleUnit = models.BooleanField(default = False, verbose_name = 'นขต.ประเมินเรียบร้อย')
    IsTroublePerson =  models.BooleanField(default = False, verbose_name = 'กพ.ทอ.ประเมินเรียบร้อย')

    def get_absolute_url(self):
        return reverse('List', kwargs={"pk": self.pk})

    def __str__(self):
        return f'{self.Requester.FullName}'

    @property
    def WorkYear(self):
        today = date.today()
        return today.year - self.PlacementDate.year

    def __str__(self):
        return f'{self.YearRound} : {self.Requester}'


# ผู้ที่พักอาศัยอยู่ร่วมกัน
class CoResident(models.Model):
    HomeRequests = models.ForeignKey(HomeRequest, on_delete=models.CASCADE, related_name='CoResident')    
    PersonID = models.CharField(max_length = 13, verbose_name="เลขประจำตัวประชาชน")
    FullName = models.CharField(max_length = 150, verbose_name="ยศ - ชื่อ - นามสกุล", null = False, blank = False, default = '')
    BirthDay = models.DateField(verbose_name="วันเกิด")
    Relation = models.CharField(max_length = 20, verbose_name="ความสัมพันธ์")
    Occupation = models.CharField(max_length = 20, verbose_name="อาชีพ")
    Salary = models.IntegerField(verbose_name="รายได้", default = 0)
    IsAirforce = models.BooleanField(verbose_name = "เป็น ขรก.ทอ.", default = False)
    Education = models.IntegerField(choices=EDUCATION_CHOICE, verbose_name="การศึกษา")

    def __str__(self):
        return self.FullName
