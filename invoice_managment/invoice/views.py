from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def invoiceList(request):
    return HttpResponse("This is the invoice list page.")