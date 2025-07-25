from django.db import models
from django.contrib.auth.models import User



# Create your models here.
class TrainerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True,null=True)
    role = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)  # Example field for user role
    postal_code = models.CharField(max_length=20, blank=True, null=True)  # Example field for user role
    bank_account_owner = models.CharField(max_length=100, blank=True, null=True) #Not to be confused with the user name
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_sort_code = models.CharField(max_length=6, blank=True, null=True)
    bank_account_number = models.CharField(max_length=8, blank=True, null=True)

    def __str__(self):
        return self.business_name  # or return self.user.get_full_name() or any field you prefer


class Client(models.Model):#ClientProfile
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    trainers = models.ManyToManyField(TrainerProfile, related_name='clients')
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    can_self_book = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_username()


class Session(models.Model):
    SESSION_TYPES = [
        ('Private', 'Private'),
        ('Group', 'Group'),
        ('Workshop', 'Workshop'),
        ('Performance', 'Performance'),
    ]
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    duration = models.DurationField(default=None, null=True, blank=True)  # Optional field for session length
    max_clients = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)

    def is_full(self):
        return self.bookings.filter(status='booked').count() >= self.max_clients
    
    def __str__(self):
        return f"{self.title} - {self.date} - {self.time} ({self.session_type})"
    

class Booking(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('invoice_generated', 'Invoice Generated'),
        ('invoice_sent', 'Invoice Sent'),
        ('invoice_paid', 'Invoice Paid'),
        ('special', 'Special'),
    ]
    session = models.ForeignKey(Session, related_name='bookings', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')

    class Meta:
        unique_together = ('session', 'client')

    def __str__(self):
        return f"{self.client.user.get_username()} - {self.session.title} - {self.session.date}- {self.session.time} - ({self.status})"

class Invoice(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE)
    bookings = models.ManyToManyField(Booking)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sent = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    special = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        self.total = sum(b.session.price for b in self.bookings.all())
        self.save()

    def __str__(self):
        return f"Invoice for {self.client.user.get_username()} - Total: {self.total} - {'Paid' if self.paid else 'Unpaid'}"


