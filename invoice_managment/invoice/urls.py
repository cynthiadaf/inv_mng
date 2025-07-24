from django.urls import path, include
from . views import InvoiceList, ClientList, SessionList, InvoiceDetail, ClientDetail, SessionDetail,InvoiceCreate,ClientCreate, SessionCreate, invoice_pdf, CustomLoginView, RegisterView, HomePageView, ClassList, ClassDetail, ClassCreate, ClientUpdate, ClassUpdate, SessionUpdate, ClientDelete, ClassDelete, SessionDelete
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),  # Home page
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  # Redirect to login after logout
    path('register/', RegisterView.as_view(), name='register'),  # Use the same view for registration
    path('invoice/', InvoiceList.as_view(), name='invoices'),
    path('invoice/<int:pk>/', InvoiceDetail.as_view(), name='invoice'),
    path('invoice/<int:pk>/pdf/', invoice_pdf, name='invoice-pdf'),
    path('client/', ClientList.as_view(), name='clients'),
    path('client/<int:pk>/', ClientDetail.as_view(), name='client'),
    path('client/create/', ClientCreate.as_view(), name='client-create'),
    path('client/<int:pk>/update/', ClientUpdate.as_view(), name='client-update'),
    path('session/', SessionList.as_view(), name='sessions'),
    path('session/<int:pk>/', SessionDetail.as_view(), name='session'),
    path('session/create/', SessionCreate.as_view(), name='session-create'),
    path('session/<int:pk>/update/', SessionUpdate.as_view(), name='session-update'),
    path('invoice/create/', InvoiceCreate.as_view(), name='invoice-create'),
    
  
    path('class/', ClassList.as_view(), name='classes'),
    path('class/<int:pk>/', ClassDetail.as_view(), name='class'),
    path('class/create/', ClassCreate.as_view(), name='class-create'),
    path('class/<int:pk>/update/', ClassUpdate.as_view(), name='class-update'),


    #path('client/', include('invoice.client.urls')),
    #path('session/', include('invoice.session.urls')),
]