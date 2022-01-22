from apps.UserData.models import User
from django.contrib.auth.models import Group

from .models import HomeData, HomeOwner, CoResident as ho_Coresident
from apps.HomeRequest.models import HomeRequest, CoResident as hr_Coresident
from apps.Utility.Constants import HomeDataStatus

def MoveFromHomeRequest(home_request):

    home_owner = HomeOwner(owner = home_request.Requester,
                            home = home_request.home_allocate,
                            is_stay = True,
                            enter_command = home_request.enter_command)
    home_owner.save()
    home_request.home_allocate.status = HomeDataStatus.STAY
    home_request.home_allocate.save()

    co_residents = [
                    ho_Coresident(
                        home_owner = home_owner,
                        person_id = cs.PersonID,
                        full_name = cs.FullName,
                        birth_day = cs.BirthDay,
                        relation = cs.Relation,
                        occupation = cs.Occupation,
                        salary = cs.Salary,
                        is_airforce = cs.IsAirforce,
                        education = cs.Education
                    )
                    for cs in home_request.CoResident.all()
                ]
    coresident = ho_Coresident.objects.bulk_create(co_residents)
    
    home_status = Group.objects.get(name='RTAF_HOME_USER')     
    home_request.Requester.groups.add(home_status)
