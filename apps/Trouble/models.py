import datetime

from django.db.models import Sum
from django.db import models

from apps.HomeRequest.models import HomeRequest
from apps.UserData.models import User


class Question(models.Model):
    class Meta:
        verbose_name_plural = "Question : คำถาม"
        ordering = ["id"]  

    Text = models.CharField(max_length = 150)

    def __str__(self):
            return f'{self.Text}'


class SetForm(models.Model):
    class Meta:
        verbose_name_plural = "SetForm : ชุดแบบฟอร์ม"

    Code = models.CharField(max_length = 20)
    Name = models.CharField(max_length = 255)
    QuestionList = models.ManyToManyField(Question, through='QuestionList')

    def __str__(self):
        return f'{self.Code} : {self.Name}'


class QuestionList(models.Model):
    class Meta:
        ordering = ["Number"]  

    Set = models.ForeignKey(SetForm, on_delete = models.CASCADE)
    Number = models.IntegerField(default = 1, verbose_name = 'ข้อที่')
    Question = models.ForeignKey(Question, on_delete = models.CASCADE)

    def __str__(self):
            return f'{self.Set.Code} : {self.Number}. {self.Question.Text}'


class Choices(models.Model):
    class Meta:
        ordering = ["Question__id", "Choice"]

    Question = models.ForeignKey(Question, on_delete = models.CASCADE)
    Choice = models.IntegerField(default = 1)
    Text = models.CharField(max_length=255)
    Score =  models.PositiveIntegerField()

    def __str__(self):
            return f'Q-id {self.Question.id} ({self.Score} คะแนน) : {self.Text} '


class FilledForm(models.Model):
    class Meta:
        # ordering = ["Question__id", "Choice"]
        verbose_name_plural = "FilledForm : ฟอร์มประเมินแล้ว"

    SetForm  = models.ForeignKey(SetForm, related_name = 'SetForm', on_delete = models.CASCADE)
    HomeRequestForm = models.ForeignKey(HomeRequest, related_name = 'HomeRequestForm', on_delete = models.CASCADE, null = True)
    TypeChoice = [('Self', 'ประเมินตนเอง'),
                  ('Unit', 'นขต.ประเมิน'),
                  ('HR', 'กพ.ทอ.ประเมิน')]

    Type = models.CharField(max_length=10,choices= TypeChoice,default='Self',)    
    Date = models.DateField(default=datetime.date.today)
    Evaluater = models.ForeignKey(User, related_name = 'Evaluater', on_delete = models.CASCADE)

    TotalScore = models.IntegerField(default = 0)

    def CalculateScore(self):
        self.TotalScore = AnsweredForm.objects.filter(
                                                FilledForm = self).values(
                                                'FilledForm').annotate(
                                                sum = Sum('ChoiceSelected__Score'))[0]['sum']
        self.save()

        return self.TotalScore

    def __str__(self):
            return f'2564-2 :[{self.Type}] : {self.HomeRequestForm.FullName}'


class AnsweredForm(models.Model):
    class Meta:
        verbose_name_plural = "AnsweredForm : รายการคำตอบ-ฟอร์มกรอกแล้ว"

    FilledForm = models.ForeignKey(FilledForm , related_name = 'AnsweredFilledForm', on_delete = models.SET_NULL, null = True)
    Question = models.ForeignKey(Question  , related_name = 'AnsweredQuestion', on_delete = models.CASCADE)
    ChoiceSelected = models.ForeignKey(Choices, 
                                        related_name = 'AnsweredChoice', 
                                        on_delete = models.CASCADE,
                                        null = True,
                                        blank = True)

    def __str__(self):
        if self.ChoiceSelected:
            return f'{self.Question.Text} - {self.ChoiceSelected.Text}'
        else:
            return self.Question.Text
