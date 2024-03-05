from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User


class UserAdmin(BaseUserAdmin):
    """Define the admin fields and options in admin panel"""

    list_display = ["pk", "username", "email", "elo_rating"]
    fieldsets = ((None, {"fields": ("username", "email", "password", "elo_rating")}),)


admin.site.register(User, UserAdmin)
