import datetime

from django.db import models

from apps.UserData.models import User

class Feedback(models.Model):
    class Meta:
        verbose_name_plural = "Feedback : ข้อเสนอแนะ"

    commenter = models.ForeignKey(User, related_name = 'commenter', on_delete = models.CASCADE)
    text = models.TextField()
    date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f"{self.date}: {self.text}"