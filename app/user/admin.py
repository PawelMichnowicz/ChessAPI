"""
Django admin customization for user.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from user.models import User

class UserAdmin(BaseUserAdmin):
    """Define the admin fields and options in admin panel"""
    list_display = [ 'pk', 'username',  'email']

admin.site.register(User, UserAdmin)

