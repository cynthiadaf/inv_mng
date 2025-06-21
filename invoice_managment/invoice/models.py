from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Invoice(models.Model):
    class Status(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        SENT = 'SENT', 'Sent'
        PAID = 'PAID', 'Paid'
        CANCELLED = 'CANCELLED', 'Cancelled'
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) #The field is optional in forms. The field can store NULL in the database if no value is provided.
    invoice_number = models.CharField(max_length=20, unique=True)
    #user data
    date = models.DateField()
    name = models.CharField(max_length=100, default="Unknown")
    role = models.CharField(max_length=100)
    address = models.TextField()
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.CREATED,
    )

    #bank data
    account_owner = models.CharField(max_length=100, blank=True, null=True) #Not to be confused with the user name
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    sort_code = models.CharField(max_length=6, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)

    #session data
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.role}"
    
    class Meta:
        ordering = ['-date','invoice_number']  # Orders by date in descending order


class Company(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']  # Orders by name in ascending order

class Session(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='sessions')
    date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    session_length = models.DurationField() # Duration of the session in hours, minutes, and seconds
    rate_per_session = models.DecimalField(max_digits=10, decimal_places=2) # Rate per session in the currency of choice
    amount = models.DecimalField(max_digits=10, decimal_places=2) # Total amount for the session


    def __str__(self):
        return f"Session {self.description} for Invoice {self.invoice.invoice_number}"
    
    class Meta:
        ordering = ['-description']  # Orders by expire date in descending order