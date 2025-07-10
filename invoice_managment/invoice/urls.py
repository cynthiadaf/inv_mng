from django.urls import path, include
from . views import InvoiceList, ClientList, SessionList, InvoiceDetail, ClientDetail, SessionDetail,InvoiceCreate,ClientCreate, SessionCreate, invoice_pdf, CustomLoginView, RegisterView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', InvoiceList.as_view(), name='invoices'),#this is for home page 
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  # Redirect to login after logout
    path('register/', RegisterView.as_view(), name='register'),  # Use the same view for registration
    path('invoice/', InvoiceList.as_view(), name='invoices'),
    path('invoice/<int:pk>/', InvoiceDetail.as_view(), name='invoice'),
    path('invoice/<int:pk>/pdf/', invoice_pdf, name='invoice-pdf'),
    path('client/', ClientList.as_view(), name='clients'),
    path('session/', SessionList.as_view(), name='sessions'),
    path('client/<int:pk>/', ClientDetail.as_view(), name='client'),
    path('session/<int:pk>/', SessionDetail.as_view(), name='session'),
    path('invoice/create/', InvoiceCreate.as_view(), name='invoice-create'),
    path('client/create/', ClientCreate.as_view(), name='client-create'),
    path('session/create/', SessionCreate.as_view(), name='session-create'),
    #path('client/', include('invoice.client.urls')),
    #path('session/', include('invoice.session.urls')),
]