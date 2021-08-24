
from django.views.generic import DetailView

from apps.HomeRequest.models import HomeRequest, CoResident

#My module
from .views import AuthenUserTestMixin

class af_person_data_detailview(AuthenUserTestMixin, DetailView):
    allow_groups = ['RTAF_NO_HOME_USER', 'PERSON_UNIT_USER','PERSON_ADMIN']
    template_name = "HomeRequest/modal_af_person.html"
    model = HomeRequest

    # def get_context_data(self, *args, **kwargs):
    #     context = super(af_person_data_detailview, self).get_context_data(*args, **kwargs)            
    #     co_residence = CoResident.objects.filter(home_request=self.object).order_by("Relation")
    #     context["co_residence"] = co_residence
    #     return context