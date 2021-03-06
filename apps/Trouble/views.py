import datetime
from datetime import date, timedelta
import requests as rq
import json


from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from apps.HomeRequest.models import HomeRequest
from apps.UserData.AFAuthentications import checkRTAFPassdword
from apps.Payment.models import FinanceData

from apps.Utility.Constants import FINANCE_CODE, HomeRequestProcessStep

from .models import ( SetForm, 
                      Question, 
                      Choices, 
                      FilledForm, 
                      QuestionList, 
                      AnsweredForm)

@login_required
def view_eval(request, HomeRequstID = 1, eval_type = 'Unit'):
    
    # # print(HomeRequstID, eval_type)
    home_request = HomeRequest.objects.get(id = HomeRequstID)
        
    set_form = SetForm.objects.get(code = 'F60')

    filled_form = FilledForm.objects.filter(set_form = set_form,
                                            home_request_form = home_request,
                                            type = eval_type)
    Troubleform = filled_form[0]        
    QAList = AnsweredForm.objects.filter(filled_form = Troubleform)
    context = {
        'Troubleform' : Troubleform,
        'QAList' : QAList
        }

    return render(request,'Trouble/list_view.html',context)

@login_required
def Evaluation(request, HomeRequstID = 1, Type = 'Self'):

    home_request = HomeRequest.objects.get(id = HomeRequstID)
    if request.POST:
        print('request.POST = ',request.POST)
        for key, value in request.POST.items():
            print(f'key = {key} value = {value}')
            if key != 'csrfmiddlewaretoken' and key != 'Troubleform':
                answer_form = AnsweredForm.objects.get(id = int(key))
                answer_form.choice_selected = Choices.objects.get(id = int(value))
                answer_form.save()
        
        TroubleformID = request.POST['Troubleform']
        filled_form = FilledForm.objects.get(id = TroubleformID)
        
        TotalScore = filled_form.CalculateScore()
        filled_form.home_request_form.TroubleScore = TotalScore
        # # print('Type = ',Type)
        if Type == 'Unit':
            filled_form.home_request_form.UnitTroubleScore = TotalScore
            filled_form.home_request_form.IsUnitEval = True
        elif Type == 'HR':
            filled_form.home_request_form.PersonTroubleScore = TotalScore
            filled_form.home_request_form.IsPersonEval = True

        filled_form.home_request_form.save()
        filled_form.save()

        messages.success(request, f'?????????????????????????????????????????????????????????????????????????????????????????????????????????????????? {home_request.FullName} ???????????????????????????????????? {TotalScore} ???????????????')


        return redirect('HomeRequest:list')
        
    set_form = SetForm.objects.get(code = 'F60')
    # _set_form = SetForm.objects.get(Code = 'F60')

    

    filled_form = FilledForm.objects.filter(set_form = set_form,
                                            home_request_form = home_request,
                                            type = Type)
    if filled_form.exists():
        filled_form[0].evaluater = request.user
        Troubleform = filled_form[0]     
    else:
        Troubleform = CreateBlankFrom(set_form, home_request, request.user, type = Type)
    
    
    QAList = AnsweredForm.objects.filter(filled_form = Troubleform)

    # # print('QAList', QAList)

    context = {
        'Troubleform' : Troubleform,
        'QAList' : QAList
        }
    return render(request,'Trouble/list_question.html',context)

def CreateBlankFrom(set_form, home_request_form, evaluater, type = 'Self', date = datetime.date.today()):
    blank_form = FilledForm(set_form = set_form,
                            home_request_form = home_request_form,
                            date = date,
                            type = type,
                            evaluater = evaluater,
                            total_score = 0)
    blank_form.save()
    
    unit_filled_form = False
    if type == 'HR':
        unit_filled_form = FilledForm.objects.filter(set_form = set_form,
                                            home_request_form = home_request_form,
                                            type = 'Unit')
        if unit_filled_form.exists():
            unit_filled_form  = unit_filled_form[0]        

    question_list = QuestionList.objects.filter(set_form = set_form)
    for question in question_list:
        answer_form = AnsweredForm(filled_form = blank_form, 
                                   question = question.question)
        if unit_filled_form:
            unit_answer = AnsweredForm.objects.filter(filled_form = unit_filled_form, question = question.question)[0]
            answer_form.choice_selected = unit_answer.choice_selected

        answer_form.save()
    
    return blank_form

    
@login_required  
def UnitEvaluation(request, HomeRequstID, view_only = 0):
    home_request = HomeRequest.objects.get(id = HomeRequstID)        
    set_form = SetForm.objects.get(code = 'F60')
    filled_form = FilledForm.objects.filter(set_form = set_form,
                                            home_request_form = home_request,
                                            type = 'Unit')
    if filled_form.exists():
        Troubleform = filled_form[0]
        # print("Troubleform = ",Troubleform)
        QAList = AnsweredForm.objects.filter(filled_form = Troubleform).order_by("question__id")
    else:
        Troubleform = CreateBlankFrom(set_form, home_request, request.user, type = 'Unit')
        QAList = AnsweredForm.objects.filter(filled_form = Troubleform).order_by("question__id")

    hris_data = loadHRISData(request,home_request.Requester.PersonID)
    hr_form_data = loadHomeRequestFormData(request,home_request)
    # print("hris_data = ",hris_data)
    data = zip(QAList, hris_data, hr_form_data)
    context = {
        'data' : data,
        'Troubleform' : Troubleform,
        'QAList' : QAList,
        'view_only': view_only == 0
        }

    return render(request,'Trouble/unit_eval.html',context)


@login_required  
def PersonEvaluation(request,HomeRequstID):
    if request.method == "POST":
        filled_form_id = int(request.POST["PersonTroubleform_id"])
        print('filled_form_id = ',filled_form_id)
        filled_form = FilledForm.objects.get(id = filled_form_id)
        
        for k, v in request.POST.items():
            print("key = ", k,"value = ", v)
            if k.isnumeric():
                answer_form = AnsweredForm.objects.get(id = int(k))
                answer_form.choice_selected = Choices.objects.get(id = int(v))
                answer_form.save()
        totalscore = filled_form.CalculateScore()
        filled_form.home_request_form.PersonTroubleScore = totalscore
        filled_form.home_request_form.IsPersonEval = True
        filled_form.home_request_form.ProcessStep = HomeRequestProcessStep.PERSON_ACCEPTED

        filled_form.home_request_form.save()
        print('totalscore = ',totalscore)
        messages.success(request,f"?????????????????????????????????????????????????????? {filled_form.home_request_form.Requester.FullName} {totalscore} ??????????????????????????????????????????")

    set_form = SetForm.objects.get(code = 'F60')
    home_request = HomeRequest.objects.get(id = HomeRequstID)        
    filled_form = FilledForm.objects.filter(set_form = set_form,
                                            home_request_form = home_request,
                                            type = 'Unit')
    if filled_form.exists():
        Troubleform = filled_form[0]
        # print("Troubleform = ",Troubleform)
        QAList = AnsweredForm.objects.filter(filled_form = Troubleform).order_by("question__id")
    else:
        blank_form = CreateBlankFrom(set_form, home_request, request.user, type = 'Unit')
        QAList = AnsweredForm.objects.filter(filled_form = blank_form).order_by("question__id")
    # ?????????????????????????????? ??????.?????????????????????????????????????????? 
    person_filled_form = FilledForm.objects.filter(set_form = set_form,
                                                home_request_form = home_request,
                                                type = 'HR')
    if person_filled_form.exists():
        person_filled_form[0].evaluater = request.user
        PersonTroubleform = person_filled_form[0]     
    else:
        PersonTroubleform = CreateBlankFrom(set_form, home_request, request.user, type = 'HR')
     
    PersonQA = AnsweredForm.objects.filter(filled_form = PersonTroubleform).order_by("question__id")

    hris_data = loadHRISData(request,home_request.Requester.PersonID)
    # print("hris_data = ",hris_data)
    data = zip(QAList, hris_data,  PersonQA)
    context = {
        'data' : data,
        'QAList' : QAList,
        'PersonTroubleform_id' : PersonTroubleform.id,
        'person_evaluate_score' : PersonTroubleform.total_score
        }

    return render(request,'Trouble/person_eval.html',context)

@login_required  
def SaveEvaluateForm(request,HomeRequstID,eval_type):
    home_request = HomeRequest.objects.get(id = HomeRequstID)        
    set_form = SetForm.objects.get(code = 'F60')
    filled_form = FilledForm.objects.filter(set_form = set_form,
                                            home_request_form = home_request,
                                            type = eval_type)
    if request.method == "POST":
        print(request.POST)
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken' and key != 'Troubleform':
                answer_form = AnsweredForm.objects.get(id = int(key))
                answer_form.choice_selected = Choices.objects.get(id = int(value))
                answer_form.save()
    if eval_type == 'Unit':
        return redirect('HomeRequest:list')

def loadHRISData(request, person_id):

    set_form = SetForm.objects.get(code = 'F60')
    question_list = QuestionList.objects.filter(set_form = set_form)
    # hris_data = ['-'] * question_list.count()
    hris_data = ['-'] * 11

    URL = "https://otp.rtaf.mi.th/api/gateway/rtaf/hris_api_1/RTAFHousePerson"


    pwd_valid = checkRTAFPassdword(request, request.user.username,request.session['password'])
    try:
        data = {
            "token" : pwd_valid['token'],
            "national_id": person_id
        } 
        # print("data = ",data)
        r = rq.post(url = URL, data = data, verify=False)
    except Exception as e:
        # print("Request Error, ",e)
        return hris_data

    return_data = json.loads(r.text)
    # # print('return_data = ',return_data)


    if return_data['result'] == "Process-Error":
        # print("Process-Error")
        return hris_data

    if return_data['data'] == "?????????????????????????????????":
        # print("?????????????????????????????????")
        return hris_data

    return_data = return_data['data'][0]
    # print(return_data)

    for i, ql in enumerate(question_list):
        if ql.question.hris_api:
            if ql.question.hris_api == "MARRIED":
                married_status = {"1" : "?????????", "2" : "????????????", "3" : "????????????", "4" : "????????????"}
                if ql.question.hris_api not in "1234":
                    hris_data[i] = "-"
                    continue                
                hris_data[i] = married_status[return_data[ql.question.hris_api]]
                if return_data[ql.question.hris_api] == "2":
                    hris_data[i] += "<br> " + str(return_data["SPOUSE_NAME"])
                    hris_data[i] += "<br> " + str(return_data["SPOUSE_IDCARD"])
            elif ql.question.hris_api == "homerent":
                homerent_data = FinanceData.objects.filter(PersonID =  person_id
                                                        ).filter(date__gte = date.today() - timedelta(days = 185)
                                                        ).filter(code = FINANCE_CODE.HOMERENT
                                                        ).filter(money__gt = 0
                                                        ).order_by("money")
            

                if(homerent_data.exists()):
                    hris_data[i] = homerent_data[0].money
                else:
                    hris_data[i] = "?????????????????????"
            elif ql.question.hris_api == "START_DATE":
                if return_data["START_DATE"]:
                    today = datetime.date.today()
                    try:
                        start_date = datetime.datetime.strptime(return_data["START_DATE"], '%Y-%m-%d %H:%M:%S.%f')
                        years = today.year - start_date.year
                        if today.month < start_date.month or (today.month == start_date.month and today.day < start_date.day):
                            years -= 1
                        hris_data[i] = f"{str(return_data['START_DATE'])[:10]} ({years} ??????)"
                    except:
                        hris_data[i] = f"{return_data['START_DATE']}"
                else:
                    hris_data[i] = "-"
            else:
                hris_data[i] = return_data[ql.question.hris_api]
        else:
            hris_data[i] = "-"
    return hris_data


def loadHomeRequestFormData(request, hr_form):

    hr_form_data = ['-'] * 11

    set_form = SetForm.objects.get(code = 'F60')
    question_list = QuestionList.objects.filter(set_form = set_form)

    for i, ql in enumerate(question_list):
        if ql.question.homerequest_field:
            if ql.question.homerequest_field == "Salary+AddSalary":
                hr_form_data[i] = hr_form.Salary 
                hr_form_data[i] += hr_form.AddSalary if hr_form.AddSalary else 0
            elif ql.question.homerequest_field == "num_coresidence":
                hr_form_data[i] = hr_form.CoResident.all().count() + 1
            else:
                field_object = HomeRequest._meta.get_field(ql.question.homerequest_field)
                # # print('field_object ' , field_object)
                # hr_form_data[i] = field_object.value_from_object(hr_form)
                try:
                    hr_form_data[i] = getattr(hr_form, f"get_{field_object.attname}_display")
                except:
                    hr_form_data[i] = getattr(hr_form, field_object.attname)

    return hr_form_data


    