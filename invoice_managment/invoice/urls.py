from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.invoiceList, name='invoices'),
]