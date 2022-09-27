from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.apps import apps

from users.models import User

class UserAdmin(BaseUserAdmin):
    """Define the admin fields and options in admin panel"""
    list_display = [ 'pk', 'username',  'email']
    fieldsets = (
        (None, {'fields': ( 'username', 'email', 'password',)}),
    )

admin.site.register(User, UserAdmin)