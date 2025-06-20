from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) #The field is optional in forms. The field can store NULL in the database if no value is provided.
    invoice_number = models.CharField(max_length=20, unique=True)
    date = models.DateField()
    company_name = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer_name}"
    
    class Meta:
        ordering = ['-date','invoice_number']  # Orders by date in descending order