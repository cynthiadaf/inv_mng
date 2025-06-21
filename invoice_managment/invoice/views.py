from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView
from .models import Invoice, Company, Session
# Create your views here.
'''def invoiceList(request):
    return HttpResponse("This is the invoice list page.")'''

class InvoiceList(ListView):
    model = Invoice
    context_object_name = 'invoices'  # Add this line

class CompanyList(ListView):
    model = Company
    context_object_name = 'companies'  # Add this line

class SessionList(ListView):
    model = Session
    context_object_name = 'sessions'  # Add this line