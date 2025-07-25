# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Client, TrainerProfile, Invoice

class TrainerRegisterForm(UserCreationForm):
    business_name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)


    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'business_name', 'email', 'phone']

class ClientRegisterForm(UserCreationForm):
    
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2',  'email', 'phone']

# forms.py
class TrainerProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = TrainerProfile
        fields = [
            'business_name', 'email', 'phone', 'address', 'postal_code', 'role',
            'bank_account_owner', 'bank_name', 'bank_sort_code', 'bank_account_number',
            # user fields are handled separately
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            profile.save()
        return profile
    

class TrainerAddClientForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    can_self_book = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class TrainerEditClientForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
   
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255, required=False)
    postal_code = forms.CharField(max_length=20, required=False)

    class Meta:
        model = Client
        fields = ['can_self_book', 'phone', 'address', 'postal_code']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        client = super().save(commit=False)
        user = client.user
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
      
        if commit:
            user.save()
            client.save()
        return client
    
class InvoiceCreateForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all(), required=True)
    date = forms.DateField(required=True, widget=forms.SelectDateWidget)


class InvoiceUpdateForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['sent', 'paid', 'special']
        widgets = {
            'sent': forms.CheckboxInput(),
            'paid': forms.CheckboxInput(),
            'special': forms.CheckboxInput(),
        }