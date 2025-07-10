from django.contrib import admin
from django.contrib.auth.models import User
from .models import Invoice, Company, Session,Client, UserProfile
admin.site.register(Company)
admin.site.register(Session)
admin.site.register(Invoice)
admin.site.register(Client)
admin.site.register(UserProfile)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline,)

# Unregister the original User admin and register your custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# Register your models here.
