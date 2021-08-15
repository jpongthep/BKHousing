from datetime import date

from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver


from apps.HomeRequest.models import HomeRequest
from apps.Utility.Constants import HomeRequestProcessStep

@receiver(post_save, sender=HomeRequest)
def HomeRequestPostSaveSignal(sender, instance, created, **kwargs):
        pass
    # if created == True:
    #     print("Signal Create New Patient exec... ")
    #     if instance.CurrentStatus > 0:
    #         print(instance.id, instance.DataUser, instance.CurrentStatus, instance.CurrentStatus)
    #         status = StatusLog(ThePatient = instance,RecorderUser = instance.DataUser,Date = instance.Date,Status = instance.CurrentStatus)
    #         status.save()

    #     if instance.CurrentTreatment > 0:
    #         treatment = TreatmentLog(ThePatient = instance, 
    #                                  RecorderUser = instance.DataUser,
    #                                  Date = instance.Date,
    #                                  Treatment = instance.CurrentTreatment)
    #         treatment.save()        



# @receiver(post_delete, sender=StatusLog)
# @receiver(post_save, sender=StatusLog)
# def StatusLogPostSaveSignal(sender, instance, **kwargs):
#     try:
#         LastestStatus = StatusLog.objects.filter(ThePatient = instance.ThePatient).order_by('-Date')
#         if LastestStatus.exists():
#             StatusResult =  LastestStatus[0].Status
#         else:
#             StatusResult = 0
        
#         patient = Patient.objects.get(id = instance.ThePatient.id)
#         patient.CurrentStatus = StatusResult
#         patient.save()
#     except:
#         print("No status")
    

# @receiver(post_delete, sender=TreatmentLog)
# @receiver(post_save, sender=TreatmentLog)
# def TreatmentLogPostSaveSignal(sender, instance, **kwargs):
#     try:
#         LastestTreatment = TreatmentLog.objects.filter(ThePatient = instance.ThePatient).order_by('-Date')
#         if LastestTreatment.exists():
#             TreatmentResult =  LastestTreatment[0].Treatment
#         else:
#             TreatmentResult = 0
        
#         patient = Patient.objects.get(id = instance.ThePatient.id)
#         patient.CurrentTreatment = TreatmentResult
#         patient.save()
#     except:
#         print("No Treatment")
 

# pre_save.connect(PreSaveSignal, sender=LeaveData)
post_save.connect(HomeRequestPostSaveSignal, sender=HomeRequest)
# post_save.connect(StatusLogPostSaveSignal, sender=StatusLog)
# post_save.connect(TreatmentLogPostSaveSignal, sender=TreatmentLog)
# pre_delete.connect(PreDeleteSignal, sender=LeaveData)
# post_delete.connect(PostDeleteSignal, sender=LeaveData)