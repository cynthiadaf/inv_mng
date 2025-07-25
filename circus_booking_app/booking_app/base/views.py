from django import forms
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
from django.contrib.auth import get_user_model


from .forms import TrainerRegisterForm, ClientRegisterForm,  TrainerAddClientForm, TrainerEditClientForm, TrainerProfileForm
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


class TrainerRegisterPage(FormView):
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
    


class ClientRegisterPage(FormView):
    template_name = 'base/register_client.html'
    form_class = ClientRegisterForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('client_dashboard')

    def form_valid(self, form):
        user = form.save()
        # Create the Client instance
        Client.objects.create(
            user=user,
            name=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            phone=form.cleaned_data['phone'],
            can_self_book=True
        )
        if user is not None:
            login(self.request, user)
            # Reload user to ensure reverse relation is available
            self.request.user = get_user_model().objects.get(pk=user.pk)
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('client_dashboard')
        return super().get(*args, **kwargs)
    
# views.py



# Utility
def client_can_book(client):
    unpaid = Invoice.objects.filter(client=client, sent=True, paid=False, special=False)
    return client.can_self_book and not unpaid.exists()


# -------- CLIENT VIEWS -------- #

class ClientDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'base/client_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'client'):
            return redirect('trainer_dashboard')
        client = Client.objects.filter(user=request.user).first()
        if not client:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = Client.objects.filter(user=self.request.user).first()
        context['client'] = client
        context['trainers'] = client.trainers.all() if client else []
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

class ClientProfileView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'base/client_profile.html'
    context_object_name = 'client'

    def get_object(self, queryset=None):
        return get_object_or_404(Client, user=self.request.user)

class ClientProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = TrainerEditClientForm
    template_name = 'base/client_form.html'
    success_url = reverse_lazy('client_profile')

    def get_object(self, queryset=None):
        return get_object_or_404(Client, user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_instance'] = self.object.user
        return kwargs
    
class ClientProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'base/client_confirm_delete.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return get_object_or_404(Client, user=self.request.user)
    

class ClientTrainerListAllView(LoginRequiredMixin, ListView):
    model = TrainerProfile
    template_name = 'base/client_trainer_list_all.html'
    context_object_name = 'trainers'

    def get_queryset(self):
        return TrainerProfile.objects.all()  # Show all trainers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = Client.objects.filter(user=self.request.user).first()
        return context
    
class ClientTrainerListView(LoginRequiredMixin, ListView):
    model = TrainerProfile
    template_name = 'base/client_trainer_list.html'
    context_object_name = 'trainers'

    def get_queryset(self):
        client = Client.objects.filter(user=self.request.user).first()
        if client:
            return client.trainers.all()  # Show trainers for this client
        return TrainerProfile.objects.none()  # No trainers if client not found
    
class ClientAddTrainerView(LoginRequiredMixin, View):
    def get(self, request):
        trainers = TrainerProfile.objects.all()
        return render(request, 'base/client_add_trainer.html', {'trainers': trainers})

    def post(self, request):
        trainer_id = request.POST.get('trainer')
        trainer = get_object_or_404(TrainerProfile, id=trainer_id)
        client = Client.objects.filter(user=request.user).first()
        if not client:
            return redirect('client-create')
        if trainer in client.trainers.all():
            messages.error(request, "Trainer already added.")
        else:
            client.trainers.add(trainer)
            messages.success(request, f"Added {trainer.user.get_full_name() or trainer.user.username} as your trainer.")
        return redirect('client_trainer_list')
    

class ClientRemoveTrainerView(LoginRequiredMixin, View):
    def get(self, request):
        client = Client.objects.filter(user=request.user).first()
        if not client:
            return redirect('client-create')
        return render(request, 'base/client_remove_trainer.html', {'client': client})

    def post(self, request):
        trainer_id = request.POST.get('trainer')
        trainer = get_object_or_404(TrainerProfile, id=trainer_id)
        client = Client.objects.filter(user=request.user).first()
        if not client:
            return redirect('client-create')
        if trainer in client.trainers.all():
            client.trainers.remove(trainer)
            messages.success(request, f"Removed {trainer.user.get_full_name() or trainer.user.username} from your trainers.")
        else:
            messages.error(request, "Trainer not found in your list.")
        return redirect('client_trainer_list')

class ClientTrainerSessionListView(LoginRequiredMixin, ListView):
    model = Session
    template_name = 'base/client_trainer_session_list.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        client = Client.objects.filter(user=self.request.user).first()
        trainer_id = self.kwargs.get('pk')
        if trainer_id:
            trainer = get_object_or_404(TrainerProfile, id=trainer_id)
            return Session.objects.filter(trainer=trainer).exclude(date__lt=timezone.now()).order_by('date', 'time')
        # If no pk, show sessions for all trainers assigned to this client
        if client:
            return Session.objects.filter(trainer__in=client.trainers.all()).exclude(date__lt=timezone.now()).order_by('trainer', 'date', 'time')
        return Session.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer_id = self.kwargs.get('pk')
        client = Client.objects.filter(user=self.request.user).first()
        if trainer_id:
            context['trainer'] = get_object_or_404(TrainerProfile, id=trainer_id)
        else:
            context['trainers'] = client.trainers.all() if client else TrainerProfile.objects.none()
        return context
    

class ClientBookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'base/client_booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        client = Client.objects.filter(user=self.request.user).first()
        if client:
            return Booking.objects.filter(client=client).select_related('session__trainer').order_by('-session__date', '-session__time')
        return Booking.objects.none()
    
class ClientBookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    fields = ['session']  # Allow client to select a session
    template_name = 'base/client_booking_form.html'
    success_url = reverse_lazy('client_booking_list')

    def dispatch(self, request, *args, **kwargs):
        self.client = Client.objects.filter(user=request.user).first()
        if not self.client:
            return redirect('client-create')
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Exclude sessions the client has already booked
        booked_sessions = Booking.objects.filter(client=self.client).values_list('session_id', flat=True)
        form.fields['session'].queryset = Session.objects.filter(
            trainer__in=self.client.trainers.all()
        ).exclude(
            date__lt=timezone.now()
        ).exclude(
            id__in=booked_sessions
        )
        return form

    def form_valid(self, form):
        form.instance.client = self.client
        session = form.instance.session
        # Check for existing booking
        if Booking.objects.filter(client=self.client, session=session).exists():
            messages.error(self.request, "You have already booked this session.")
            return redirect('client_booking_list')
        if not client_can_book(self.client):
            messages.error(self.request, "You cannot book sessions at this time.")
            return redirect('client_dashboard')
        if session.is_full():
            messages.error(self.request, "This session is full.")
            return redirect('client_trainer_session_list')
        return super().form_valid(form)


    



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

        if Booking.objects.filter(client=client, session=session).exists():
            messages.error(request, "You have already booked this session.")
            return redirect('client_dashboard')

        Booking.objects.create(client=client, session=session, status='booked')
        messages.success(request, f"Booked {session.title} successfully.")
        return redirect('client_dashboard')
    
class ClientBookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'base/client_booking_detail.html'
    context_object_name = 'booking'

    def get_object(self, queryset=None):
        booking = super().get_object(queryset)
        if booking.client.user != self.request.user:
            raise HttpResponseForbidden("You do not have permission to view this booking.")
        return booking
    
class ClientBookingUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    fields = ['session']  # Allow client to change session or status
    template_name = 'base/client_booking_form.html'
    success_url = reverse_lazy('client_booking_list')

    def get_object(self, queryset=None):
        booking = super().get_object(queryset)
        if booking.client.user != self.request.user:
            raise HttpResponseForbidden("You do not have permission to edit this booking.")
        return booking

    def form_valid(self, form):
        if not client_can_book(form.instance.client):
            messages.error(self.request, "You cannot modify bookings at this time.")
            return redirect('client_dashboard')
        return super().form_valid(form)
    
class ClientBookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    template_name = 'base/client_booking_confirm_delete.html'
    success_url = reverse_lazy('client_booking_list')

    def get_object(self, queryset=None):
        booking = super().get_object(queryset)
        if booking.client.user != self.request.user:
            raise HttpResponseForbidden("You do not have permission to delete this booking.")
        return booking

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Booking deleted successfully.")
        return super().delete(request, *args, **kwargs)


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
        context['trainer'] = trainer
        return context

class TrainerProfileView(LoginRequiredMixin, DetailView):
    model = TrainerProfile
    template_name = 'base/trainer_profile.html'
    context_object_name = 'trainer'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        if pk:
            return get_object_or_404(TrainerProfile, pk=pk)
        return get_object_or_404(TrainerProfile, user=self.request.user)


class TrainerProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = TrainerProfile
    form_class = TrainerProfileForm
    template_name = 'base/trainer_profile_form.html'
    success_url = reverse_lazy('trainer_profile')

    def get_object(self, queryset=None):
        return get_object_or_404(TrainerProfile, user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_instance'] = self.request.user
        return kwargs
    
class TrainerProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = TrainerProfile
    template_name = 'base/trainer_profile_confirm_delete.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return get_object_or_404(TrainerProfile, user=self.request.user)
    


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
    
class TrainerAddExistingClientView(LoginRequiredMixin, FormView):
    template_name = 'base/trainer_add_existing_client.html'
    success_url = reverse_lazy('trainer_client_list')

    def get_form(self):
        # Dynamically create a form with a dropdown of all clients not already assigned to this trainer
        class ExistingClientForm(forms.Form):
            client = forms.ModelChoiceField(
                queryset=Client.objects.exclude(trainers=self.request.user.trainerprofile),
                required=True,
                label="Select Existing Client"
            )
        return ExistingClientForm(self.request.POST or None)

    def form_valid(self, form):
        client = form.cleaned_data['client']
        trainer_profile = self.request.user.trainerprofile
        client.trainers.add(trainer_profile)
        messages.success(self.request, f"{client.user.get_full_name() or client.user.username} added to your client list.")
        return super().form_valid(form)
    
class TrainerRemoveExistingClientView(LoginRequiredMixin, View):
    """
    Allows a trainer to remove an existing client from their client list.
    If no pk is provided, shows a form to select a client to remove.
    """
    def get(self, request, pk=None):
        trainer_profile = request.user.trainerprofile
        if pk is None:
            # Show a form to select a client to remove
            clients = Client.objects.filter(trainers=trainer_profile)
            return render(request, 'base/trainer_remove_client_select.html', {'clients': clients})
        client = get_object_or_404(Client, pk=pk)
        return render(request, 'base/trainer_remove_client_confirm.html', {'client': client})

    def post(self, request, pk=None):
        trainer_profile = request.user.trainerprofile
        if pk is None:
            # Get client id from form submission and redirect to confirmation
            client_id = request.POST.get('client_id')
            if not client_id:
                messages.error(request, "No client selected.")
                return redirect('trainer_client_remove')
            return redirect('trainer_client_remove', pk=client_id)
        client = get_object_or_404(Client, pk=pk)
        if trainer_profile in client.trainers.all():
            client.trainers.remove(trainer_profile)
            messages.success(request, f"{client.user.get_full_name() or client.user.username} has been removed from your client list.")
        else:
            messages.error(request, "This client is not assigned to you.")
        return redirect('trainer_client_list')
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
        # Only clients for this trainer not already booked for this session
        already_booked = Booking.objects.filter(session=self.session).values_list('client_id', flat=True)
        self.clients_qs = Client.objects.filter(trainers=request.user.trainerprofile).exclude(id__in=already_booked)
        if not self.clients_qs.exists():
            messages.error(request, "You have no available clients to add to this session.")
            return redirect('session_detail', pk=self.session.id)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['client'].queryset = self.clients_qs
        return form

    def form_valid(self, form):
        client = form.cleaned_data['client']
        # Check if session is full
        if self.session.is_full():
            messages.error(self.request, "Session is full.")
            return redirect('session_detail', pk=self.session.id)
        unpaid = Invoice.objects.filter(client=client, sent=True, paid=False, special=False).exists()
        if unpaid:
            messages.error(self.request, "Client has unpaid invoices.")
            return redirect('session_detail', pk=self.session.id)
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
    
class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'base/booking_detail.html'
    context_object_name = 'booking'

    def get_object(self, queryset=None):
        booking = super().get_object(queryset)
        if booking.session.trainer != self.request.user.trainerprofile:
            raise HttpResponseForbidden("You do not have permission to view this booking.")
        return booking
    
class BookingUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    fields = ['client', 'session', 'status']
    template_name = 'base/booking_form.html'
    success_url = reverse_lazy('booking_list')

    def get_object(self, queryset=None):
        booking = super().get_object(queryset)
        if booking.session.trainer != self.request.user.trainerprofile:
            raise HttpResponseForbidden("You do not have permission to edit this booking.")
        return booking

    def form_valid(self, form):
        session = form.cleaned_data['session']
        client = form.cleaned_data['client']

        if session.is_full() and form.instance.status == 'booked':
            messages.error(self.request, "Session is full.")
            return redirect('booking_edit', pk=form.instance.id)

        unpaid = Invoice.objects.filter(client=client, sent=True, paid=False, special=False).exists()
        if unpaid:
            messages.error(self.request, "Client has unpaid invoices.")
            return redirect('booking_edit', pk=form.instance.id)

        return super().form_valid(form)
    
class BookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    template_name = 'base/booking_confirm_delete.html'
    success_url = reverse_lazy('booking_list')

    def get_object(self, queryset=None):
        booking = super().get_object(queryset)
        if booking.session.trainer != self.request.user.trainerprofile:
            raise HttpResponseForbidden("You do not have permission to delete this booking.")
        return booking



