import datetime

from django.db.models import Sum
from django.db import models

from apps.HomeRequest.models import HomeRequest
from apps.UserData.models import User
from apps.Utility.Constants import FillFormTypeChoice


class Question(models.Model):
    class Meta:
        verbose_name_plural = "Question : คำถาม"
        ordering = ["id"]  

    text = models.CharField(max_length = 150)

    def __str__(self):
            return f'{self.text}'


class SetForm(models.Model):
    class Meta:
        verbose_name_plural = "SetForm : ชุดแบบฟอร์ม"

    code = models.CharField(max_length = 20)
    name = models.CharField(max_length = 255)
    question_list = models.ManyToManyField(Question, through='QuestionList')

    def __str__(self):
        return f'{self.code} : {self.name}'


class QuestionList(models.Model):
    class Meta:
        ordering = ["number"]  

    set_form = models.ForeignKey(SetForm, on_delete = models.CASCADE)
    number = models.IntegerField(default = 1, verbose_name = 'ข้อที่')
    question = models.ForeignKey(Question, on_delete = models.SET_NULL, null = True)

    def __str__(self):
            return f'{self.set_form.code} : {self.number}. {self.question.text}'


class Choices(models.Model):
    class Meta:
        ordering = ["question__id", "choice"]

    question = models.ForeignKey(Question, on_delete = models.CASCADE)
    choice = models.IntegerField(default = 1)
    text = models.CharField(max_length=255)
    score =  models.PositiveIntegerField()

    def __str__(self):
            return f'Q-id {self.question.id} ({self.score} คะแนน) : {self.text} '


class FilledForm(models.Model):
    class Meta:
        verbose_name_plural = "FilledForm : ฟอร์มประเมินแล้ว"

    set_form  = models.ForeignKey(SetForm, related_name = 'SetForm', on_delete = models.CASCADE)
    home_request_form = models.ForeignKey(HomeRequest, related_name = 'HomeRequestForm', on_delete = models.CASCADE, null = True)
    type = models.CharField(max_length=10,choices= FillFormTypeChoice,default='Self',)    
    date = models.DateField(default=datetime.date.today)
    evaluater = models.ForeignKey(User, related_name = 'Evaluater', on_delete = models.CASCADE)

    total_score = models.IntegerField(default = 0)

    def CalculateScore(self):
        total_score = AnsweredForm.objects.filter(filled_form = self
                                                ).values('filled_form'
                                                ).annotate(sum = Sum('choice_selected__score')
                                                ).aggregate(Sum('sum'))['sum__sum']

        self.total_score =  total_score
        self.save()

        return total_score

    def __str__(self):
            return f'2564-2 :[{self.type}] : {self.home_request_form.FullName}'


class AnsweredForm(models.Model):
    class Meta:
        verbose_name_plural = "AnsweredForm : รายการคำตอบ-ฟอร์มกรอกแล้ว"
        ordering = ["question__id"]        

    filled_form = models.ForeignKey(FilledForm , related_name = 'AnsweredFilledForm', on_delete = models.SET_NULL, null = True)
    question = models.ForeignKey(Question  , related_name = 'AnsweredQuestion', on_delete = models.CASCADE)
    choice_selected = models.ForeignKey(Choices, 
                                        related_name = 'AnsweredChoice', 
                                        on_delete = models.CASCADE,
                                        null = True,
                                        blank = True)

    def __str__(self):
        if self.choice_selected:
            return f'{self.question.text} - {self.choice_selected.text}'
        else:
            return self.question.text
