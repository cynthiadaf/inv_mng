from django.contrib import admin

from .models import TrainerProfile, Client, Session, Booking, Invoice

# Register your models here.
admin.site.register(TrainerProfile)
admin.site.register(Client)
admin.site.register(Session)
admin.site.register(Booking)
admin.site.register(Invoice)

class TrainerProfileInline(admin.StackedInline):
    model = TrainerProfile
    can_delete = False
    verbose_name_plural = 'Trainer Profile' 

class UserAdmin(admin.ModelAdmin):
    inlines = (TrainerProfileInline,)   
