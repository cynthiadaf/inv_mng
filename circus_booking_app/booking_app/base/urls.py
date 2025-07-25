from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),  # Home page   
    

    # Trainer
    path('trainer/dashboard/', views.TrainerDashboardView.as_view(), name='trainer_dashboard'),
    path('trainer/profile/', views.TrainerProfileView.as_view(), name='trainer_profile'),
    path('trainer/profile/edit/', views.TrainerProfileUpdateView.as_view(), name='trainer_profile_edit'),
    path('trainer/profile/delete/', views.TrainerProfileDeleteView.as_view(), name='trainer_profile_delete'),
    path('trainer/profile/<int:pk>/', views.TrainerProfileView.as_view(), name='trainer_profile_detail'),
    
    path('trainer/client/', views.TrainerClientListView.as_view(), name='trainer_client_list'),
    path('trainer/client/create/', views.TrainerClientCreateView.as_view(), name='trainer_client_create'),
    
    #path('trainer/client/add-existing/', views.TrainerAddExistingClientView.as_view(), name='trainer_add_existing_client'), #trainer add existing client 
    path('trainer/client/<int:pk>/', views.TrainerClientDetailView.as_view(), name='trainer_client_detail'),
    path('trainer/client/<int:pk>/edit/', views.TrainerClientUpdateView.as_view(), name='trainer_client_edit'),
    path('trainer/client/<int:pk>/delete/', views.TrainerClientDeleteView.as_view(), name='trainer_client_delete'),
    path('trainer/client/add/', views.TrainerAddExistingClientView.as_view(), name='trainer_client_add'),
    path('trainer/client/remove/', views.TrainerRemoveExistingClientView.as_view(), name='trainer_client_remove'),
    path('trainer/client/remove/<int:pk>/', views.TrainerRemoveExistingClientView.as_view(), name='trainer_client_remove'),

    path('trainer/session/', views.TrainerSessionListView.as_view(), name='trainer_session_list'),
    path('trainer/session/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('trainer/session/create/', views.SessionCreateView.as_view(), name='session_create'),
    path('trainer/session/<int:pk>/edit/', views.SessionUpdateView.as_view(), name='session_edit'),
    path('trainer/session/<int:pk>/delete/', views.SessionDeleteView.as_view(), name='session_delete'),
    path('trainer/session/<int:pk>/booking/', views.SessionBookingListView.as_view(), name='session_booking_list'),
    path('trainer/session/<int:pk>/booking/create', views.SessionBookingCreateView.as_view(), name='session_booking_create'),
    #path('trainer/session/<int:session_id>/add-client/<int:client_id>/', views.AddClientBookingView.as_view(), name='add_client_booking'),

    #Bookings
    path('trainer/bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('trainer/bookings/create/', views.BookingCreateView.as_view(), name='booking_create'),
    path('trainer/bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('trainer/bookings/<int:pk>/edit/', views.BookingUpdateView.as_view(), name='booking_edit'),
    path('trainer/bookings/<int:pk>/delete/', views.BookingDeleteView.as_view(), name='booking_delete'),


    #Invoices
    path('trainer/invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('trainer/invoices/create/', views.InvoiceCreateView.as_view(), name='invoice_create'),
    path('trainer/invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('trainer/invoices/<int:pk>/edit/', views.InvoiceUpdateView.as_view(), name='invoice_edit'),
    path('trainer/invoices/<int:pk>/delete/', views.InvoiceDeleteView.as_view(), name='invoice_delete'),
    path('trainer/invoices/<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    # Client
    path('client/profile/', views.ClientProfileView.as_view(), name='client_profile'),
    path('client/profile/edit/', views.ClientProfileUpdateView.as_view(), name='client_profile_edit'),
    path('client/profile/delete/', views.ClientProfileDeleteView.as_view(), name='client_profile_delete'),
    path('client/dashboard/', views.ClientDashboardView.as_view(), name='client_dashboard'),

    path('client/trainers/all/', views.ClientTrainerListAllView.as_view(), name='client_trainer_list_all'),
    path('client/trainers/', views.ClientTrainerListView.as_view(), name='client_trainer_list'),
    path('client/trainers/<int:pk>/session/', views.ClientTrainerSessionListView.as_view(), name='client_trainer_session_list'),
    path('client/trainers/session/', views.ClientTrainerSessionListView.as_view(), name='client_trainer_session_list'),
    path('client/trainers/add/', views.ClientAddTrainerView.as_view(), name='client_add_trainer'),
    path('client/trainers/add/<int:pk>/', views.ClientAddTrainerView.as_view(), name='client_add_trainer'),
    path('client/trainers/remove/<int:pk>/', views.ClientRemoveTrainerView.as_view(), name='client_remove_trainer'),
    path('client/trainers/remove/', views.ClientRemoveTrainerView.as_view(), name='client_remove_trainer'),

    path('client/bookings/', views.ClientBookingListView.as_view(), name='client_booking_list'),
    path('client/bookings/create/', views.ClientBookingCreateView.as_view(), name='client_booking_create'),
    path('client/session/<int:pk>/book/', views.ClientBookSessionView.as_view(), name='client_book_session'),
    
    path('client/bookings/<int:pk>/', views.ClientBookingDetailView.as_view(), name='client_booking_detail'),
    path('client/bookings/<int:pk>/edit/', views.ClientBookingUpdateView.as_view(), name='client_booking_edit'),
    path('client/bookings/<int:pk>/delete/', views.ClientBookingDeleteView.as_view(), name='client_booking_delete'),


    #path('client/book/<int:pk>/', views.ClientBookSessionView.as_view(), name='book_session'),
    path('client/invoices/', views.ClientInvoiceListView.as_view(), name='client_invoices'),
    path('client/create/', views.ClientSelfCreateView.as_view(), name='client-create'),


    #Invoices

    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/trainer/', views.TrainerRegisterPage.as_view(), name='register-trainer'),
    path('register/client/', views.ClientRegisterPage.as_view(), name='register-client'),
 

]