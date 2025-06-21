from django.urls import path, include
from . views import InvoiceList, CompanyList, SessionList
#from .views import 

urlpatterns = [
    path('', InvoiceList.as_view(), name='invoices'),
    path('company/', CompanyList.as_view(), name='companies'),
    path('session/', SessionList.as_view(), name='sessions'),
    #path('company/', include('invoice.company.urls')),
    #path('session/', include('invoice.session.urls')),
]