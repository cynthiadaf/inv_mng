from django.contrib import admin
from .models import Invoice, Company, Session
admin.site.register(Company)
admin.site.register(Session)
admin.site.register(Invoice)
# Register your models here.
