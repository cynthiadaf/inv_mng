from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Personal Data
    
    role = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField()
    postal_code = models.CharField(max_length=20, blank=True, null=True)  # Example field for user role
    account_owner = models.CharField(max_length=100, blank=True, null=True) #Not to be confused with the user name
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    sort_code = models.CharField(max_length=6, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
# Create your models here.
class Invoice(models.Model):
    class Status(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        SENT = 'SENT', 'Sent'
        PAID = 'PAID', 'Paid'
        CANCELLED = 'CANCELLED', 'Cancelled'
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) #The field is optional in forms. The field can store NULL in the database if no value is provided.
    #invoice_number = models.CharField(max_length=20, unique=True)
    #user data
    date = models.DateField()
    name = models.CharField(max_length=100)  # Default to the username of the user
    role = models.CharField(max_length=100,default='')  # Default to the role of the user
    address = models.TextField(default='')
    postal_code = models.CharField(max_length=20,default='')  # Default to an empty string if not provided
    email = models.EmailField(default='email@example.com')  # Default to the email of the user
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.CREATED,
    )

    #bank data
    account_owner = models.CharField(max_length=100,default='') #Not to be confused with the user name
    bank_name = models.CharField(max_length=100,default='')
    sort_code = models.CharField(max_length=6,default='')
    account_number = models.CharField(max_length=20, default='')  # Default to an empty string if not provided

    #session data
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='invoices', null=True, blank=True)
    sessions = models.ManyToManyField('Session', related_name='invoices', blank=True)
    # ...rest of your model...

    def update_total_amount(self):
        total = sum(session.amount for session in self.sessions.all())
        if self.total_amount != total:
            Invoice.objects.filter(pk=self.pk).update(total_amount=total)
            self.total_amount = total

    def save(self, *args, **kwargs):
        # Auto-populate fields from user and user.profile if not set
        if self.user:
            if not self.name:
                self.name = self.user.username
            if hasattr(self.user, 'profile'):
                profile = self.user.profile
                if not self.role:
                    self.role = profile.role
                if not self.address:
                    self.address = profile.address
                if not self.postal_code:
                    self.postal_code = profile.postal_code
                if not self.email:
                    self.email = self.user.email
                if not self.account_owner:
                    self.account_owner = profile.account_owner
                if not self.bank_name:
                    self.bank_name = profile.bank_name
                if not self.sort_code:
                    self.sort_code = profile.sort_code
                if not self.account_number:
                    self.account_number = profile.account_number
        super().save(*args, **kwargs)
     
      
        
        self.update_total_amount()

    def __str__(self):
        return f"Invoice {self.id} - {self.role}"
    
    class Meta:
        ordering = ['-date']  # Orders by date in descending order


class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']  # Orders by name in ascending order

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sessions', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    session_length = models.DurationField() # Duration of the session in hours, minutes, and seconds
    rate_per_session = models.DecimalField(max_digits=10, decimal_places=2) # Rate per session in the currency of choice
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.rate_per_session
        super().save(*args, **kwargs)
        # Update total_amount for all invoices of this client
        for invoice in self.client.invoices.all():
            invoice.update_total_amount()


    def __str__(self):
        return f"Session {self.description} for Invoice "
    
    class Meta:
        ordering = ['-description']  # Orders by expire date in descending order