from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),  # Home page   
    

    # Trainer
    path('trainer/dashboard/', views.TrainerDashboardView.as_view(), name='trainer_dashboard'),
    
    path('trainer/client/', views.TrainerClientListView.as_view(), name='trainer_client_list'),
    path('trainer/client/create/', views.TrainerClientCreateView.as_view(), name='trainer_client_create'),
    
    #path('trainer/client/add-existing/', views.TrainerAddExistingClientView.as_view(), name='trainer_add_existing_client'), #trainer add existing client 
    path('trainer/client/<int:pk>/', views.TrainerClientDetailView.as_view(), name='trainer_client_detail'),
    path('trainer/client/<int:pk>/edit/', views.TrainerClientUpdateView.as_view(), name='trainer_client_edit'),
    path('trainer/client/<int:pk>/delete/', views.TrainerClientDeleteView.as_view(), name='trainer_client_delete'),

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
    # Client
    path('client/dashboard/', views.ClientDashboardView.as_view(), name='client_dashboard'),
    path('client/book/<int:pk>/', views.ClientBookSessionView.as_view(), name='book_session'),
    path('client/invoices/', views.ClientInvoiceListView.as_view(), name='client_invoices'),
    path('client/create/', views.ClientSelfCreateView.as_view(), name='client-create'),

    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/trainer/', views.RegisterPage.as_view(), name='register-trainer'),
 

]