#python module
import os
from io import StringIO, BytesIO
#django Module
from django.shortcuts import render
from django.views.generic import CreateView, ListView, DetailView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.conf import settings

#3rd party module
from docx import Document
from docx.shared import Inches

#My module
from .models import HomeRequest
from .forms import HomeRequestForm, CoResidentFormSet

class CreateHomeRequestView(CreateView):
    model = HomeRequest
    form_class = HomeRequestForm
    template_name = "HomeRequest/CreateHomeRequest.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        co_resident_formset = CoResidentFormSet()
        return self.render_to_response(
                                self.get_context_data(form=form,
                                                        co_resident_formset=co_resident_formset,
                                                        ))    

    def post(self, request, *args, **kwargs):
        self.object = None
        # form_class = self.get_form_class()
        # form = self.get_form(form_class)
        form = self.form_class(request.POST, request.FILES)

        co_resident_formset = CoResidentFormSet(self.request.POST)
        if form.is_valid() and co_resident_formset.is_valid():
            return self.form_valid(form, co_resident_formset)
        else:
            return self.form_invalid(form, co_resident_formset)

    def form_valid(self, form, co_resident_formset):
        self.object = form.save(commit=False)        
        self.object.Requester = self.request.user
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

class HomeRequestListView(ListView):
    model = HomeRequest    
    template_name = "HomeRequest/list.html"

class HomeRequestUnitListView(ListView):
    model = HomeRequest    
    template_name = "Person/unit_summary.html"

class HomeRequestDetail(DetailView):
    model = HomeRequest
    template_name = "HomeRequest/Detail.html"


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