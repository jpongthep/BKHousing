import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse

from apps.HomeRequest.models import HomeRequest
from .models import ( SetForm, 
                      Question, 
                      Choices, 
                      FilledForm, 
                      QuestionList, 
                      AnsweredForm)


def view_eval(request, HomeRequstID = 1, eval_type = 'Unit'):
    
    print(HomeRequstID, eval_type)
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

def Evaluation(request, HomeRequstID = 1, Type = 'Self'):

    home_request = HomeRequest.objects.get(id = HomeRequstID)
    if request.POST:
        print('request.POST = ',request.POST)
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken' and key != 'Troubleform':
                answer_form = AnsweredForm.objects.get(id = int(key))
                answer_form.choice_selected = Choices.objects.get(id = int(value))
                answer_form.save()
        
        TroubleformID = request.POST['Troubleform']
        filled_form = FilledForm.objects.get(id = TroubleformID)
        
        TotalScore = filled_form.CalculateScore()
        filled_form.home_request_form.TroubleScore = TotalScore
        print('Type = ',Type)
        if Type == 'Unit':
            filled_form.home_request_form.UnitTroubleScore = TotalScore
            filled_form.home_request_form.IsUnitEval = True
        elif Type == 'Person':
            filled_form.home_request_form.PersonTroubleScore = TotalScore
            filled_form.home_request_form.IsPersonEval = True

        filled_form.home_request_form.save()
        filled_form.save()

        messages.success(request, f'บันทึกข้อมูลการประเมินความเดือดร้อนของ {home_request.FullName} เรียบร้อยได้ {TotalScore} คะแนน')


        return redirect('HomeRequest:list')
        
    set_form = SetForm.objects.get(code = 'F60')
    # _set_form = SetForm.objects.get(Code = 'F60')

    

    filled_form = FilledForm.objects.filter(set_form = set_form,
                                            home_request_form = home_request,
                                            evaluater = request.user)
    if filled_form.exists():
        Troubleform = filled_form[0]        
    else:
        Troubleform = CreateBlankFrom(set_form, home_request, request.user, type = Type)
    
    
    QAList = AnsweredForm.objects.filter(filled_form = Troubleform)

    # print('QAList', QAList)

    context = {
        'Troubleform' : Troubleform,
        'QAList' : QAList
        }
    return render(request,'Trouble/list_question.html',context)

def CreateBlankFrom(set_form, home_request_form, evaluater, type = 'Self', date = datetime.date.today()):
    blank_form = FilledForm( 
                            set_form = set_form,
                            home_request_form = home_request_form,
                            date = date,
                            type = type,
                            evaluater = evaluater,
                            total_score = 0)
    blank_form.save()
    
    question_list = QuestionList.objects.filter(set_form = set_form)
    for question in question_list:
        answer_form = AnsweredForm(filled_form = blank_form, 
                                   question = question.question)
        answer_form.save()
    
    return blank_form

    
    
    