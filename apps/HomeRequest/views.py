#python module
import os
from io import StringIO, BytesIO
#django Module
from django.shortcuts import render
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.conf import settings

from django.db.models import Q, F
from django.db.models import Count, Sum, Max

#3rd party module
from docx import Document
from openpyxl import load_workbook

#My module
from .models import HomeRequest, CoResident
from .forms import HomeRequestForm, CoResidentFormSet
from apps.Utility.Constants import (YEARROUND_PROCESSSTEP, HomeRequestProcessStep)
from apps.Configurations.models import YearRound


def get_current_year():
    CurrentYearRound = YearRound.objects.filter(Q(CurrentStep = YEARROUND_PROCESSSTEP.REQUEST_SENDED) 
                                                        | Q(CurrentStep = YEARROUND_PROCESSSTEP.UNIT_PROCESS)
                                                        | Q(CurrentStep = YEARROUND_PROCESSSTEP.PERSON_PROCESS))

    CurrentYear = CurrentYearRound[0].Year
    return CurrentYear

class HousingUserPassesTestMixin(UserPassesTestMixin):
    allow_groups = []

    def test_func(self):
        for ag in self.allow_groups:
            if self.request.user.groups.filter(name=ag).exists():
                return True
                
        return False


class CreateHomeRequestView(CreateView):
    model = HomeRequest
    form_class = HomeRequestForm
    template_name = "HomeRequest/CreateHomeRequest.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        # form_class = self.get_form_class()
        # form = self.get_form(form_class)

        initial_value = {
                            'Rank': request.user.Rank,
                            'FullName': request.user.FullName,
                            'Position': request.user.Position,
                            'Unit': request.user.CurrentUnit,
                            'OfficePhone' : request.user.OfficePhone
                        }        
        form = self.form_class(initial = initial_value)

        co_resident_formset = CoResidentFormSet()
        return self.render_to_response(
                                self.get_context_data(form=form,
                                                        co_resident_formset=co_resident_formset,
                                                        ))    

    # def get(self, request, *args, **kwargs):

    #     form = self.form_class(initial = initial_value)
    #     return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.form_class(request.POST, request.FILES)

        co_resident_formset = CoResidentFormSet(self.request.POST)
        if form.is_valid() and co_resident_formset.is_valid():
            return self.form_valid(form, co_resident_formset)
        else:
            return self.form_invalid(form, co_resident_formset)

    def form_valid(self, form, co_resident_formset):
        self.object = form.save(commit=False)    
        # กำหนดค่าเริ่มต้นให้ form    
        self.object.Requester = self.request.user
        CurrentYearRound = YearRound.objects.filter(Q(CurrentStep = YEARROUND_PROCESSSTEP.REQUEST_SENDED) 
                                                        | Q(CurrentStep = YEARROUND_PROCESSSTEP.UNIT_PROCESS)
                                                        | Q(CurrentStep = YEARROUND_PROCESSSTEP.PERSON_PROCESS))

        self.object.YearRound = CurrentYearRound[0]
        self.object.Unit = self.request.user.CurrentUnit
        self.object.ProcessStep = HomeRequestProcessStep.REQUESTER_PROCESS
        self.object.save()

        co_resident = co_resident_formset.save(commit=False)
        for cr in co_resident:
            cr.home_request = self.object
            cr.save()
            
        messages.success(self.request, f'เพิ่มข้อมูลบ้านพักของ {self.object.FullName} เรียบร้อย')

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, co_resident_formset):

        return self.render_to_response(
                 self.get_context_data(form=form,
                                       co_resident_formset=co_resident_formset
                                       )
        )

class UpdateHomeRequestView(UpdateView):
    model = HomeRequest
    form_class = HomeRequestForm
    template_name = "HomeRequest/CreateHomeRequest.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        co_resident_formset = CoResidentFormSet(instance=self.object)

        return self.render_to_response(
                  self.get_context_data(form = HomeRequestForm(instance=self.object),
                                        co_resident_formset = co_resident_formset,
                                        )
                                     )

    
class AFPersonListView(LoginRequiredMixin, HousingUserPassesTestMixin,ListView):
    login_url = '/login'
    template_name = "HomeRequest/af_person.html"
    allow_groups = ['RTAF_NO_HOME_USER']

    def get_queryset(self):
        queryset = HomeRequest.objects.filter(Requester = self.request.user)
        queryset = queryset.order_by("-year_round__Year")
        return queryset


class HomeRequestUnitListView(LoginRequiredMixin, HousingUserPassesTestMixin, ListView):
    login_url = '/login'
    model = HomeRequest    
    template_name = "HomeRequest/list.html"
    allow_groups = ['PERSON_ADMIN', 'PERSON_UNIT_USER']

    def get_queryset(self, *args, **kwargs):

        if self.request.user.groups.filter(name='PERSON_UNIT_USER').exists():
                queryset = HomeRequest.objects.filter(Unit = self.request.user.CurrentUnit)                
        
        if 'unit_id' in self.kwargs:
            unit_id =  self.kwargs['unit_id']
            if self.request.user.groups.filter(name='PERSON_ADMIN').exists():
                    queryset = HomeRequest.objects.filter(Unit_id = unit_id)
        
        queryset = queryset.filter(year_round__Year = get_current_year())
        queryset = queryset.order_by("-year_round__Year")
        return queryset    


class HomeRequestUnitSummaryListView(LoginRequiredMixin, HousingUserPassesTestMixin,ListView):
    login_url = '/login' 
    template_name = "Person/unit_summary.html"
    allow_groups = ['PERSON_ADMIN']

    def get_queryset(self):

        Num_RP = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.REQUESTER_PROCESS))
        Num_RS = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.REQUESTER_SENDED))
        Num_UP = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.UNIT_PROCESS))
        Num_US = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.UNIT_SENDED))
        Num_PP = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.PERSON_PROCESS))
        Num_PR = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.PERSON_REPORTED))
        Num_GH = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.GET_HOUSE))
        DateSended = Max('UnitDateApproved')
        UnitApprover = Max('UnitApprover__first_name')
        
        queryset = HomeRequest.objects.filter(year_round__Year = get_current_year())

        queryset = queryset.exclude(
                                    Q(ProcessStep = HomeRequestProcessStep.REQUESTER_CANCEL) 
                                ).values('Unit'
                                ).annotate(
                                    DateSended = DateSended,
                                    UnitApprover = UnitApprover,
                                    Num_RP = Num_RP,
                                    Num_RS = Num_RS,
                                    Num_UP = Num_UP,
                                    Num_US = Num_US,
                                    Num_PP = Num_PP,
                                    Num_PR = Num_PR,
                                    Num_GH = Num_GH
                                ).values(
                                    'Unit',
                                    'Unit__ShortName',
                                    'DateSended',
                                    'UnitApprover',
                                    'Num_RP',
                                    'Num_RS',
                                    'Num_UP',
                                    'Num_US',
                                    'Num_PP',
                                    'Num_PR',
                                    'Num_GH'
                                )
        
        return queryset

class HomeRequestDetail(DetailView):
    model = HomeRequest
    template_name = "HomeRequest/Detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(HomeRequestDetail, self).get_context_data(*args, **kwargs)            
        co_residence = CoResident.objects.filter(home_request=self.object)
        context["co_residence"] = co_residence
        return context


def TestDocument(request,home_request_id):

    # testdoc = static('documents/test_doc.docx')
    testdoc =  os.path.join(settings.TEMPLATES[0]['DIRS'][0],'documents/test_doc.docx')

    document = Document(testdoc)

    home_request = HomeRequest.objects.get(id = home_request_id)
    docx_title= f"House-{home_request.Requester.AFID}.docx"

    time_and_date = "2019-10-21"
    employee_name = home_request.FullName
    manager_name = "Michelle Johnson"
    if home_request.Unit:
        department_name = home_request.Unit.FullName
    else:
        department_name = "ยังไม่ระบุ"

    # replace function
    def find_replace(paragraph_keyword, draft_keyword, paragraph):
        if paragraph_keyword in paragraph.text:
            paragraph.text = paragraph.text.replace(paragraph_keyword, draft_keyword)

    #replace #my_sentense# with our sentense
    for paragraph in document.paragraphs:
        find_replace("#time_and_date#", time_and_date, paragraph)
        find_replace("#employee_name#", employee_name, paragraph)
        find_replace("#manager_name#", manager_name, paragraph)
        find_replace("#department_name#", department_name, paragraph)

    # Prepare document for download        
    # -----------------------------
    f = BytesIO()
    document.save(f)
    length = f.tell()
    f.seek(0)
    response = HttpResponse(
        f.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    print('docx_title = ',docx_title)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(docx_title)
    response['Content-Length'] = length
    return response


def TestExcel(request,unit_id):

    # testdoc = static('documents/test_doc.docx')
    testxls =  os.path.join(settings.TEMPLATES[0]['DIRS'][0],'documents/test_xls.xlsx')

    # Start by opening the spreadsheet and selecting the main sheet
    workbook = load_workbook(filename=testxls)
    xls_title= f"Unit.xlsx"

    sheet = workbook.active

    # Write what you want into a specific cell
    sheet["D1"] = "writing ;)"

    # Save the spreadsheet

    # Prepare document for download        
    # -----------------------------
    f = BytesIO()
    
    workbook.save(f)
    length = f.tell()
    f.seek(0)
    response = HttpResponse(
        f.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    print('xls = ',xls_title)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(xls_title)
    response['Content-Length'] = length
    return response    