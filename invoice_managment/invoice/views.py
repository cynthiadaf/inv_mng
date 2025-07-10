from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.forms import inlineformset_factory
from django import forms
from .models import Invoice, Client, Session
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate

# Create your views here.

#https://stackoverflow.com/questions/62935406/how-to-make-a-signup-view-using-class-based-views-in-django ?

class CustomUserCreationForm(UserCreationForm):
    role = forms.CharField(max_length=50, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    postal_code = forms.CharField(max_length=20, required=False)
    account_owner = forms.CharField(max_length=100, required=False)
    bank_name = forms.CharField(max_length=100, required=False)
    sort_code = forms.CharField(max_length=6, required=False)
    account_number = forms.CharField(max_length=20, required=False)
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'address', 'postal_code', 'account_owner', 'bank_name', 'sort_code', 'account_number']

class RegisterView(FormView):
    template_name = 'invoice/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('invoices')
    redirect_authenticated_user = True  # Redirect to home page if user is already authenticated
    '''This view handles user registration.
    It uses a custom user creation form and redirects to the invoices page upon successful registration.'''
    def form_valid(self, form):
        user = form.save()
        # Save profile fields
        profile = user.profile
        profile.role = form.cleaned_data.get('role')
        profile.address = form.cleaned_data.get('address')
        profile.postal_code = form.cleaned_data.get('postal_code')
        profile.account_owner = form.cleaned_data.get('account_owner')
        profile.bank_name = form.cleaned_data.get('bank_name')
        profile.sort_code = form.cleaned_data.get('sort_code')
        profile.account_number = form.cleaned_data.get('account_number')
        profile.save()
        login(self.request, user)
        return super().form_valid(form)

class CustomLoginView(LoginView):
    template_name = 'invoice/login.html'  # Specify your login template here
    fields = '__all__'  # Include all fields in the form
    redirect_authenticated_user = True  # Redirect to home page if user is already authenticated
    
    def get_success_url(self):
        return reverse_lazy('invoices')  # Redirect to invoices page after successful login
#logout view is handled by Django's built-in LogoutView, so no need to define it here.



class InvoiceList(LoginRequiredMixin, ListView):
    model = Invoice
    context_object_name = 'invoices'  # Add this line
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoices'] = context['invoices'].filter(user=self.request.user)  # Filter invoices by the logged-in user
        return context

class ClientList(LoginRequiredMixin, ListView):
    model = Client
    context_object_name = 'clients'  # Add this line
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = context['clients'].filter(user=self.request.user)  # Filter clients by the logged-in user
        return context

class SessionList(LoginRequiredMixin, ListView):
    model = Session
    context_object_name = 'sessions'  # Add this line
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = context['sessions'].filter(user=self.request.user)  # Filter sessions by the logged-in user
        return context

class InvoiceDetail(LoginRequiredMixin, DetailView):
    model = Invoice
    context_object_name = 'invoice'
    template_name = 'invoice/invoice.html'  # Specify the template name if needed


class ClientDetail(LoginRequiredMixin, DetailView):
    model = Client
    context_object_name = 'client'
    template_name = 'invoice/client.html'  # Specify the template name if needed

class SessionDetail(LoginRequiredMixin, DetailView):
    model = Session
    context_object_name = 'session'
    template_name = 'invoice/session.html'  # Specify the template name if needed

'''The following classes are used to create, update, and delete invoices, companies, and sessions.
These classes inherit from Django's generic views to handle the respective operations.'''

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['date', 'sessions']
        widgets = {
            'sessions': forms.SelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['sessions'].queryset = Session.objects.filter(user=user)
class InvoiceCreate(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoice/invoice_form.html'
    success_url = reverse_lazy('invoices')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        sessions = form.cleaned_data.get('sessions')
        if sessions:
            self.object.sessions.set(sessions)
            # Set client from the first session (all sessions should have the same client)
            session_client = sessions.first().client if sessions.exists() else None
            if session_client and self.object.client != session_client:
                self.object.client = session_client
                self.object.save(update_fields=['client'])
            self.object.update_total_amount()
        return response
    
   

class ClientCreate(LoginRequiredMixin,CreateView):
    model = Client
    fields = ['name', 'address', 'phone', 'email']  # Replace with your actual fields
    success_url = '/client/'

    

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ClientCreate, self).form_valid(form)

class SessionCreate(LoginRequiredMixin,CreateView):
    model = Session
    fields = ['client', 'description', 'location', 'quantity', 'session_length', 'rate_per_session']
    success_url = '/session/'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only show clients for the current user
        form.fields['client'].queryset = Client.objects.filter(user=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(SessionCreate, self).form_valid(form)

class InvoiceUpdate(LoginRequiredMixin,UpdateView):
    model = Invoice
    fields = ['field1', 'field2', ...]  # Replace with your actual fields
    success_url = '/invoices/'

class ClientUpdate(LoginRequiredMixin,UpdateView):
    model = Client
    fields = ['field1', 'field2', ...]  # Replace with your actual fields
    success_url = '/clients/'

class SessionUpdate(LoginRequiredMixin,UpdateView):
    model = Session
    fields = ['field1', 'field2', ...]  # Replace with your actual fields
    success_url = '/sessions/'

class InvoiceDelete(LoginRequiredMixin,DeleteView):
    model = Invoice
    success_url = '/invoices/'

class ClientDelete(LoginRequiredMixin,DeleteView):
    model = Client
    success_url = '/clients/'

class SessionDelete(DeleteView):
    model = Session
    success_url = '/sessions/'


'''
This function renders a template to a PDF response using xhtml2pdf.`
The render function takes a template source and a context dictionary,
and returns an HttpResponse with the generated PDF. currently it will output the invoice as a PDF file styled with the html
'''
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def invoice_pdf(request, pk):
    invoice = Invoice.objects.get(pk=pk)
    context = {'invoice': invoice}
    return render_to_pdf('invoice/invoice.html', context)