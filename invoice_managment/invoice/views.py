from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.forms import inlineformset_factory
from .models import Invoice, Client, Session
from xhtml2pdf import pisa
from django.template.loader import get_template
# Create your views here.
'''def invoiceList(request):
    return HttpResponse("This is the invoice list page.")'''

class InvoiceList(ListView):
    model = Invoice
    context_object_name = 'invoices'  # Add this line

class ClientList(ListView):
    model = Client
    context_object_name = 'clients'  # Add this line

class SessionList(ListView):
    model = Session
    context_object_name = 'sessions'  # Add this line

class InvoiceDetail(DetailView):
    model = Invoice
    context_object_name = 'invoice'
    template_name = 'invoice/invoice.html'  # Specify the template name if needed

class ClientDetail(DetailView):
    model = Client
    context_object_name = 'client'
    template_name = 'invoice/client.html'  # Specify the template name if needed

class SessionDetail(DetailView):
    model = Session
    context_object_name = 'session'
    template_name = 'invoice/session.html'  # Specify the template name if needed

'''The following classes are used to create, update, and delete invoices, companies, and sessions.
These classes inherit from Django's generic views to handle the respective operations.'''
class InvoiceCreate(CreateView):
    model = Invoice
    fields = '__all__'  # add '__all__' to include all fields
    template_name = 'invoice/invoice_form.html'
    success_url = reverse_lazy('invoices')
    
    
    

class ClientCreate(CreateView):
    model = Client
    fields = '__all__'  # Replace with your actual fields
    success_url = '/client/'

class SessionCreate(CreateView):
    model = Session
    fields = ['client', 'description', 'location', 'quantity', 'session_length', 'rate_per_session']
    success_url = '/session/'

class InvoiceUpdate(UpdateView):
    model = Invoice
    fields = ['field1', 'field2', ...]  # Replace with your actual fields
    success_url = '/invoices/'

class ClientUpdate(UpdateView):
    model = Client
    fields = ['field1', 'field2', ...]  # Replace with your actual fields
    success_url = '/clients/'

class SessionUpdate(UpdateView):
    model = Session
    fields = ['field1', 'field2', ...]  # Replace with your actual fields
    success_url = '/sessions/'

class InvoiceDelete(DeleteView):
    model = Invoice
    success_url = '/invoices/'

class ClientDelete(DeleteView):
    model = Client
    success_url = '/clients/'

class SessionDelete(DeleteView):
    model = Session
    success_url = '/sessions/'


'''
This function renders a template to a PDF response using xhtml2pdf.`
The render function takes a template source and a context dictionary,
and returns an HttpResponse with the generated PDF. currently it will output the invoice as a PDF file styled with the html
'''
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def invoice_pdf(request, pk):
    invoice = Invoice.objects.get(pk=pk)
    context = {'invoice': invoice}
    return render_to_pdf('invoice/invoice.html', context)