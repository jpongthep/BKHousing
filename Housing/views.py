import requests as rq
from django.views.generic import TemplateView

class LandingTemplate(TemplateView):
    template_name = "landing.html"

def daily_notify_message():
    line_notify_token = "klXrp9gFaCxXWZUfWoUNgr2UWF2DshKExui61zLbKno" # ARMIS
    line_notify_token = "klXrp9gFaCxXWZUfWoUNgr2UWF2DshKExui61zLbKno" #Doc Dog Tutor
   
    url = 'https://notify-api.line.me/api/notify'
    headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer ' + line_notify_token}
    # r = rq.post(url, headers=headers, data = {'message': 'ทดสอบส่งข้อความ เวลา '})
    # print(r.text)


