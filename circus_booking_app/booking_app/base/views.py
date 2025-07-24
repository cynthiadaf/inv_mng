from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View, FormView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from .models import Session, Client, Booking, Invoice
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


from .forms import TrainerRegisterForm,  TrainerAddClientForm, TrainerEditClientForm
from .models import TrainerProfile


class HomePageView(TemplateView):
    template_name = 'base/home.html'


# ------------ AUTHENTICATION VIEWS ------------ #

class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'trainerprofile'):
            return reverse_lazy('trainer_dashboard')
        elif hasattr(user, 'client'):
            return reverse_lazy('client_dashboard')
        return reverse_lazy('home')


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = TrainerRegisterForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        # Create TrainerProfile
        TrainerProfile.objects.create(
            user=user,
            business_name=form.cleaned_data['business_name'],
            email=form.cleaned_data['email'],
            phone=form.cleaned_data['phone']
        )
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home')
        return super().get(*args, **kwargs)
    
# views.py



# Utility
def client_can_book(client):
    unpaid = Invoice.objects.filter(client=client, sent=True, paid=False, special=False)
    return client.can_self_book and not unpaid.exists()


# -------- CLIENT VIEWS -------- #

class ClientDashboardView(LoginRequiredMixin, TemplateView):
    model = Client
    template_name = 'base/client_dashboard.html'
   
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'client'):
            return redirect('trainer_dashboard')
        client = Client.objects.filter(user=request.user).first()
        if not client:
            return redirect('home') #TODO: redirect to a logical page
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = Client.objects.filter(user=self.request.user).first()
        context['client'] = client
        # Trainers for this client
        context['trainers'] = client.trainers.all() if client else []
        # Sessions for this client
        #context['sessions'] = Session.objects.filter(clients=client) if client else []

        return context
   
    '''
    def get_queryset(self):
        # You can filter sessions as needed, e.g., only future sessions, not full, etc.
        return Session.objects.all()

    def dispatch(self, request, *args, **kwargs):
        client = Client.objects.filter(user=request.user).first()
        if not client:
            return redirect('client-create')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = Client.objects.filter(user=self.request.user).first()
        return context
    '''
 
class ClientSelfCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ['can_self_book', 'trainers']  # allow user to select trainers if desired
    template_name = 'base/client_form.html'
    success_url = reverse_lazy('client_dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ClientBookSessionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        client = Client.objects.filter(user=request.user).first()
        if not client:
            return redirect('client-create')
        session = get_object_or_404(Session, id=pk)

        if not client_can_book(client):
            messages.error(request, "You're not allowed to book sessions.")
            return redirect('client_dashboard')

        if session.is_full():
            messages.error(request, "This session is full.")
            return redirect('client_dashboard')

        Booking.objects.get_or_create(client=client, session=session, defaults={'status': 'booked'})
        messages.success(request, f"Booked {session.title} successfully.")
        return redirect('client_dashboard')


class ClientInvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'client_invoices.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        return Invoice.objects.filter(client=self.request.user.client)


# -------- TRAINER VIEWS -------- #
''''
class TrainerDashboardView(LoginRequiredMixin, ListView):
    model = Session
    template_name = 'trainer_dashboard.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        return Session.objects.filter(trainer=self.request.user.trainerprofile)
'''
class TrainerDashboardView(LoginRequiredMixin, TemplateView):
    '''
    Trainer dashboard view that shows all sessions and clients for the trainer.They can also view bookings and create invoices from here
    
    '''
    template_name = 'base/trainer_dashboard.html'
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'trainerprofile'):
            return redirect('client_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer = self.request.user.trainerprofile
        context['sessions'] = Session.objects.filter(trainer=trainer)
        context['clients'] = Client.objects.filter(trainers=trainer)
        return context
    
class TrainerClientCreateView(LoginRequiredMixin, FormView):
    template_name = 'base/client_form.html'
    form_class = TrainerAddClientForm
    success_url = reverse_lazy('trainer_dashboard')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email = form.cleaned_data['email']
        user.first_name = form.cleaned_data.get('first_name', '')
        user.last_name = form.cleaned_data.get('last_name', '')
        user.save()
        client = Client.objects.create(
            user=user,
            can_self_book=form.cleaned_data.get('can_self_book', False)
        )
        client.trainers.add(self.request.user.trainerprofile)
        # Optionally, send credentials to the client via email here
        return super().form_valid(form)
    

class TrainerClientListView(LoginRequiredMixin, ListView):
    '''
    List all clients for the trainer.'''
    model = Client
    template_name = 'base/trainer_client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        return Client.objects.filter(trainers=self.request.user.trainerprofile)
    
class TrainerClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'base/trainer_client_detail.html'
    context_object_name = 'client'

    def get_object(self, queryset=None):
        return get_object_or_404(Client, id=self.kwargs['pk'], trainers=self.request.user.trainerprofile)
    

class TrainerClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = TrainerEditClientForm
    template_name = 'base/client_form.html'
    success_url = reverse_lazy('trainer_client_list')

    def get_object(self, queryset=None):
        return get_object_or_404(Client, id=self.kwargs['pk'], trainers=self.request.user.trainerprofile)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_instance'] = self.object.user
        return kwargs
    
class TrainerClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'base/client_confirm_delete.html'
    success_url = reverse_lazy('trainer_client_list')

    def get_object(self, queryset=None):
        # Only allow deletion if the client belongs to this trainer
        return get_object_or_404(Client, id=self.kwargs['pk'], trainers=self.request.user.trainerprofile)


class TrainerSessionListView(LoginRequiredMixin, ListView):
    model = Session
    template_name = 'base/trainer_session_list.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        return Session.objects.filter(trainer=self.request.user.trainerprofile)
    
class SessionDetailView(LoginRequiredMixin, DetailView):
    model = Session
    template_name = 'base/session_detail.html'
    context_object_name = 'session'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_object()
        context['bookings'] = session.bookings.select_related('client')
        return context


class SessionCreateView(LoginRequiredMixin, CreateView):
    model = Session
    fields = ['title', 'date', 'time', 'duration', 'max_clients', 'price', 'session_type']
    template_name = 'base/session_form.html'
    success_url = reverse_lazy('trainer_session_list')

    def form_valid(self, form):
        form.instance.trainer = self.request.user.trainerprofile
        return super().form_valid(form)


class SessionUpdateView(LoginRequiredMixin, UpdateView):
    model = Session
    fields = ['title', 'date', 'time', 'duration', 'max_clients', 'price', 'session_type']
    template_name = 'base/session_form.html'
    success_url = reverse_lazy('trainer_session_list')


class SessionDeleteView(LoginRequiredMixin, DeleteView):
    model = Session
    template_name = 'base/session_confirm_delete.html'
    success_url = reverse_lazy('trainer_session_list')

class SessionBookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'base/session_booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        session = get_object_or_404(Session, id=self.kwargs['pk'], trainer=self.request.user.trainerprofile)
        return session.bookings.select_related('client')
    

class SessionBookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    fields = ['client']  # Trainer selects which client to add
    template_name = 'base/booking_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.session = get_object_or_404(Session, id=self.kwargs['pk'], trainer=request.user.trainerprofile)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit clients to those assigned to this trainer and not already booked for this session
        already_booked = Booking.objects.filter(session=self.session).values_list('client_id', flat=True)
        form.fields['client'].queryset = Client.objects.filter(trainers=self.request.user.trainerprofile).exclude(id__in=already_booked)
        return form

    def form_valid(self, form):
        client = form.cleaned_data['client']
        # Check if session is full
        if self.session.is_full():
            messages.error(self.request, "Session is full.")
            return redirect('session_detail', pk=self.session.id)
        # Check for unpaid invoices
        unpaid = Invoice.objects.filter(client=client, sent=True, paid=False, special=False).exists()
        if unpaid:
            messages.error(self.request, "Client has unpaid invoices.")
            return redirect('session_detail', pk=self.session.id)
        # Create booking
        form.instance.session = self.session
        form.instance.status = 'booked'
        messages.success(self.request, f"{client.user.get_full_name() or client.user.username} successfully booked.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('session_detail', kwargs={'pk': self.session.id})


#Bookings

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'base/booking_list.html'
    context_object_name = 'bookings'
    def get_queryset(self):
        return Booking.objects.filter(session__trainer=self.request.user.trainerprofile).select_related('client', 'session')


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    fields = ['client', 'session']
    template_name = 'base/booking_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only sessions for this trainer that are not full
        sessions = Session.objects.filter(trainer=self.request.user.trainerprofile)
        available_sessions = [s.id for s in sessions if not s.is_full()]
        form.fields['session'].queryset = sessions.filter(id__in=available_sessions)
        # Only clients for this trainer
        form.fields['client'].queryset = Client.objects.filter(trainers=self.request.user.trainerprofile)
        return form

    def form_valid(self, form):
        session = form.cleaned_data['session']
        client = form.cleaned_data['client']

        if session.trainer != self.request.user.trainerprofile:
            messages.error(self.request, "You can only book clients into your own sessions.")
            return redirect('booking_create')

        if client not in form.fields['client'].queryset:
            messages.error(self.request, "You can only book your own clients.")
            return redirect('booking_create')

        if session.is_full():
            messages.error(self.request, "Session is full.")
            return redirect('session_detail', pk=session.id)

        unpaid = Invoice.objects.filter(client=client, sent=True, paid=False, special=False).exists()
        if unpaid:
            messages.error(self.request, "Client has unpaid invoices.")
            return redirect('session_detail', pk=session.id)

        form.instance.session = session
        form.instance.client = client
        form.instance.status = 'booked'
        messages.success(self.request, f"{client.user.get_full_name() or client.user.username} successfully booked for {session.title}.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('booking_list')


'''
class AddClientBookingView(LoginRequiredMixin, View):
    def post(self, request, session_id, client_id):
        trainer = request.user.trainerprofile
        session = get_object_or_404(Session, id=session_id, trainer=trainer)
        client = get_object_or_404(Client, id=client_id, trainers=trainer)

        if session.is_full():
            messages.error(request, "Session is full.")
            return redirect('session_detail', pk=session_id)

        unpaid = Invoice.objects.filter(client=client, sent=True, paid=False, special=False).exists()
        if unpaid:
            messages.error(request, "Client has unpaid invoices.")
            return redirect('session_detail', pk=session_id)

        Booking.objects.get_or_create(client=client, session=session, defaults={'status': 'booked'})
        messages.success(request, "Client successfully booked.")
        return redirect('session_detail', pk=session_id)
'''

