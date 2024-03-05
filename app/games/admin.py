from django.contrib import admin
from .models import Challange, Game


# Register your models here.
@admin.register(Challange)
class ChallangeAdmin(admin.ModelAdmin):
    """Define admin panel for action model"""

    list_display = ["pk", "from_user", "to_user", "status"]


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Define admin panel for action model"""

    list_display = ["pk", "winner", "loser"]
