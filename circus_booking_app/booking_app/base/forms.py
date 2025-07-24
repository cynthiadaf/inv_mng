# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Client

class TrainerRegisterForm(UserCreationForm):
    business_name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'business_name', 'email', 'phone']



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

    class Meta:
        model = Client
        fields = ['can_self_book']

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