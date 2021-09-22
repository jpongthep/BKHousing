#python module
import os
from io import StringIO, BytesIO
#django Module
from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
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
from apps.UserData.models import Unit
from apps.Configurations.models import YearRound
from apps.UserData.forms import UserCurrentDataForm


def get_current_year():
    CurrentYearRound = YearRound.objects.filter(Q(CurrentStep = YEARROUND_PROCESSSTEP.REQUEST_SENDED) 
                                              | Q(CurrentStep = YEARROUND_PROCESSSTEP.UNIT_PROCESS)
                                              | Q(CurrentStep = YEARROUND_PROCESSSTEP.PERSON_PROCESS))
    CurrentYear = CurrentYearRound[0].Year
    # print('CurrentYear = ',CurrentYear)
    return CurrentYear


class AuthenUserTestMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/login' 
    allow_groups = []

    def test_func(self):
        for ag in self.allow_groups:
            if self.request.user.groups.filter(name=ag).exists():
                return True
        return False

    def has_home_request(self):
        queryset = HomeRequest.objects.filter(Requester = self.request.user)
        queryset = queryset.filter(year_round__Year = get_current_year())
        return queryset.exists()


class ProcessFlow(TemplateView):
    template_name = "HomeRequest/process_flow.html"

class CreateHomeRequestView(AuthenUserTestMixin, CreateView):
    allow_groups = ['RTAF_NO_HOME_USER']
    model = HomeRequest
    form_class = HomeRequestForm
    template_name = "HomeRequest/CreateHomeRequest.html"

    # ทดสอบเพิ่มเติมว่าถ้าปีนี้มีการส่งคำขอแล้ว ก็ส่งอีกไม่ได้
    def test_func(self):
        if super().test_func() == False:
            return False
        else:
            return not super().has_home_request()

    def get(self, request, *args, **kwargs):
        self.object = None
        # form_class = self.get_form_class()
        # form = self.get_form(form_class)
        initial_value = {
                            'Rank': request.user.Rank,
                            'FullName': request.user.FullName,
                            'Position': request.user.Position,
                            'Unit': request.user.CurrentUnit,
                            'OfficePhone' : request.user.OfficePhone,
                            'Unit' : request.user.CurrentUnit,
                            'Salary' : request.user.current_salary,
                            'Status' : request.user.current_status,
                            'SpouseName' : request.user.current_spouse_name,
                            'SpousePID' : request.user.current_spouse_pid,
                            'Address' : request.user.Address
                        }        
        form = self.form_class(initial = initial_value, prefix='hr')

        co_resident_formset = CoResidentFormSet()

        initial_value = {
                            'OfficePhone' : request.user.OfficePhone,
                            'MobilePhone' : request.user.MobilePhone,
                        }        
        user_current_data_form =  UserCurrentDataForm(initial = initial_value, prefix='userdata')
        return self.render_to_response(
                                self.get_context_data(form=form,
                                                      co_resident_formset=co_resident_formset,
                                                      user_current_data_form = user_current_data_form
                                                        ))    

    # def get(self, request, *args, **kwargs):

    #     form = self.form_class(initial = initial_value)
    #     return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.form_class(request.POST, request.FILES, prefix='hr')

        user_current_data_form = UserCurrentDataForm(self.request.POST, prefix='userdata')
        co_resident_formset = CoResidentFormSet(self.request.POST)
        if form.is_valid() and co_resident_formset.is_valid():
            return self.form_valid(form, user_current_data_form, co_resident_formset)
        else:
            return self.form_invalid(form, user_current_data_form, co_resident_formset)

    def form_valid(self, form, user_current_data_form, co_resident_formset):
        self.object = form.save(commit=False)
        # กำหนดค่าเริ่มต้นให้ form    
        self.object.Requester = self.request.user
        CurrentYearRound = YearRound.objects.filter(Q(CurrentStep = YEARROUND_PROCESSSTEP.REQUEST_SENDED) 
                                                  | Q(CurrentStep = YEARROUND_PROCESSSTEP.UNIT_PROCESS)
                                                  | Q(CurrentStep = YEARROUND_PROCESSSTEP.PERSON_PROCESS))

        self.object.year_round = CurrentYearRound[0]
        self.object.Unit = self.request.user.CurrentUnit
        self.object.ProcessStep = HomeRequestProcessStep.REQUESTER_PROCESS
        self.object.save()
        
        # user_current_data_form.save()

        co_resident = co_resident_formset.save(commit=False)
        for cr in co_resident:
            cr.home_request = self.object
            cr.save()

        messages.success(self.request, f'เพิ่มข้อมูลบ้านพักของ {self.object.FullName} เรียบร้อย')

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, co_resident_formset):
        print(form.errors)
        return self.render_to_response(
                 self.get_context_data(form=form,
                                       co_resident_formset=co_resident_formset
                                       )
        )

class UpdateHomeRequestView(AuthenUserTestMixin, UpdateView):
    allow_groups = ['RTAF_NO_HOME_USER']
    model = HomeRequest
    form_class = HomeRequestForm
    template_name = "HomeRequest/CreateHomeRequest.html"

    #ในกรณีที่ส่งรายงานแล้ว จะไม่สามารถแก้ไขข้อมูลได้
    def test_func(self):
        if super().test_func() == False:
            return False
        else:
            self.object = self.get_object()
            return not self.object.RequesterSended

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        home_request = self.object
        
        co_resident_formset = CoResidentFormSet(instance = home_request, 
                                                queryset = home_request.CoResident.order_by("Relation"))

        print("update -> get method ")

        return self.render_to_response(
                  self.get_context_data(form = HomeRequestForm(instance=self.object, prefix='hr'),
                                        user_current_data_form =  UserCurrentDataForm(instance = request.user, prefix='userdata'),
                                        co_resident_formset = co_resident_formset
                                        )
                                       )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        print('get_context_data kwargs = ',kwargs)
        if self.request.POST:
            data['form'] = HomeRequestForm(self.request.POST, prefix='hr')
            data["user_current_data_form"] = UserCurrentDataForm(self.request.POST, prefix='userdata')
            data["co_resident"] = CoResidentFormSet(self.request.POST, instance=self.object)
        else:
            data['form'] = HomeRequestForm(instance=self.object, prefix='hr')
            data["user_current_data_form"] = UserCurrentDataForm(instance = self.request.user, prefix='userdata')
            data["co_resident"] = CoResidentFormSet(instance=self.object)
        # print('data = ',data)
        return data

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance = self.object, prefix='hr')

        user_current_data_form = UserCurrentDataForm(self.request.POST, instance = request.user, prefix='userdata')
        co_resident_formset = CoResidentFormSet(self.request.POST)
        if form.is_valid() and user_current_data_form.is_valid() and co_resident_formset.is_valid():
            return self.form_valid(form, user_current_data_form, co_resident_formset)
        else:
            return self.form_invalid(form, user_current_data_form, co_resident_formset)

    def form_valid(self, form, user_current_data_form, co_resident_formset):

        user_current_data_form.save()
        co_resident = co_resident_formset.save(commit=False)

        for cr in co_resident:
            cr.home_request = self.object
            cr.save()

        if 'save' in self.request.POST:
            messages.info(self.request, f'บันทึกการแก้ไขข้อมูลบ้านพักของ {self.object.FullName} เรียบร้อย')
        elif 'send' in self.request.POST:
            self.object.update_process_step(
                                    HomeRequestProcessStep.REQUESTER_SENDED, 
                                    self.request.user)
            self.object.save()
            messages.success(self.request, f'บันทึกการแก้ไขและส่งข้อมูลบ้านพักของ {self.object.FullName} เรียบร้อย')

        return super().form_valid(form)

    def form_invalid(self, form, user_current_data_form, co_resident_formset):
        print("="*60)
        print('form_invalid => formerrors  ',form.errors)
        print('co_resident_formset => co_resident_formseterrors  ',co_resident_formset.errors)
        return super().form_invalid(form)

    def get_success_url(self):        
        return reverse('HomeRequest:af_person')


class AFPersonListView(AuthenUserTestMixin,ListView):
    template_name = "HomeRequest/af_person.html"
    allow_groups = ['RTAF_NO_HOME_USER']

    def get_queryset(self):
        queryset = HomeRequest.objects.filter(Requester = self.request.user)
        queryset = queryset.order_by("-year_round__Year")
        return queryset

    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)
        context['has_request'] = super().has_home_request(**kwargs)
        return context        


class HomeRequestUnitListView(AuthenUserTestMixin, ListView):
    model = HomeRequest    
    template_name = "HomeRequest/list.html"
    allow_groups = ['PERSON_ADMIN', 'PERSON_UNIT_ADMIN']

    def get_queryset(self, *args, **kwargs):

        if self.request.user.groups.filter(name='PERSON_UNIT_ADMIN').exists():
                queryset = HomeRequest.objects.filter(Unit = self.request.user.CurrentUnit)                
        
        if 'unit_id' in self.kwargs:
            unit_id =  self.kwargs['unit_id']
            if self.request.user.groups.filter(name='PERSON_ADMIN').exists():
                    queryset = HomeRequest.objects.filter(Unit_id = unit_id)
        
        queryset = queryset.filter(year_round__Year = get_current_year())
        queryset = queryset.order_by("-year_round__Year")
        return queryset 
    
    def get_template_names(self):
        if "hr/ul" in self.request.META.get('HTTP_REFERER'):
            return "Person/modal_list.html"
        else:
            return "HomeRequest/list.html"


class HomeRequestUnitSummaryListView(AuthenUserTestMixin,ListView):
    template_name = "Person/unit_summary.html"
    allow_groups = ['PERSON_ADMIN']

    def get_queryset(self):

        Num_RP = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.REQUESTER_PROCESS))
        Num_RS = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.REQUESTER_SENDED))
        Num_UP = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.UNIT_PROCESS))
        Num_US = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.UNIT_SENDED))
        Num_PP = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.PERSON_PROCESS))
        Num_PA = Count('ProcessStep', filter = Q(ProcessStep = HomeRequestProcessStep.PERSON_ACCEPTED))
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
                                    Num_PA = Num_PA,
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
                                    'Num_PA',
                                    'Num_GH'
                                )
        
        return queryset

class HomeRequestDetail(AuthenUserTestMixin, DetailView):
    allow_groups = ['RTAF_NO_HOME_USER','PERSON_UNIT_ADMIN']
    model = HomeRequest
    template_name = "HomeRequest/Detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(HomeRequestDetail, self).get_context_data(*args, **kwargs)            
        co_residence = CoResident.objects.filter(home_request=self.object).order_by("Relation")
        context["co_residence"] = co_residence
        return context


@login_required
def update_process_step(request, home_request_id, process_step):
    allow_groups = ['PERSON_ADMIN', 'PERSON_UNIT_ADMIN']
    allow_access = False
    for ag in allow_groups:
        if request.user.groups.filter(name=ag).exists():
            allow_access = True
            break
    if not allow_access:
        raise PermissionDenied()
               
    home_request = HomeRequest.objects.get(id = home_request_id)
    unit_id = home_request.Unit.id
    home_request.ProcessStep = process_step
    home_request.save()
    home_request.update_process_step(process_step, request.user)
    print("sdfdsf")

    if process_step in [ HomeRequestProcessStep.UNIT_PROCESS, 
                         HomeRequestProcessStep.UNIT_SENDED]:
        return HttpResponseRedirect("/hr/list")
    elif process_step in [ HomeRequestProcessStep.PERSON_PROCESS, 
                           HomeRequestProcessStep.PERSON_ACCEPTED]:
        return HttpResponseRedirect(f"/hr/{unit_id}/list")


def TestDocument(request,home_request_id):
    # testdoc = static('documents/test_doc.docx')
    testdoc =  os.path.join(settings.TEMPLATES[0]['DIRS'][0],'documents/request_data.docx')

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
    dic = {
            'FullName':home_request.FullName,
            'PersonID':home_request.Requester.PersonID,
            'Position':home_request.Position,
            'UnitFN':home_request.Unit.FullName,
            'UnitStN':home_request.Unit.ShortName,
            'OfficePhone':home_request.Requester.OfficePhone,
            'MobilePhone':home_request.Requester.MobilePhone,
            'AddSalary':"{:,}".format(home_request.AddSalary),
            'Salary':"{:,}".format(home_request.Salary),
            
            }
    print(dic)

    for para in document.paragraphs:
        for key, value in dic.items():
            if key in para.text:
                inline = para.runs
                # Loop added to work with runs (strings with same style)
                for i in range(len(inline)):
                    if key in inline[i].text:
                        text = inline[i].text.replace(key, value)
                        inline[i].text = text

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
    testxls =  os.path.join(settings.TEMPLATES[0]['DIRS'][0],'documents/unit_report.xlsx')
    # Start by opening the spreadsheet and selecting the main sheet
    workbook = load_workbook(filename=testxls)
    xls_title= f"unit_report.xlsx"

    sheet = workbook.active

    # Write what you want into a specific cell
    sheet["A1"] = f'หน่วย {request.user.CurrentUnit.ShortName}'

    
    xls_unit = Unit.objects.get(id = unit_id)

    queryset = HomeRequest.objects.filter(Unit = xls_unit)
    
    # if request.user.groups.filter(name='PERSON_ADMIN').exists():
    #     queryset = HomeRequest.objects.filter(Unit_id = unit_id)
    
    queryset = queryset.filter(year_round__Year = get_current_year())
    queryset = queryset.order_by("-year_round__Year")
    first_row = 6
    for i, data in enumerate(queryset):
        sheet[f"A{first_row+i}"] = i+1
        sheet[f"B{first_row+i}"] = data.FullName
        sheet[f"C{first_row+i}"] = data.get_Status_display()
        sheet[f"D{first_row+i}"] = data.Salary + data.AddSalary
        sheet[f"R{first_row+i}"] = data.Requester.MobilePhone


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