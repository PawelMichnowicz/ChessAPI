from django.contrib import admin
from .models import Challange, Player

# Register your models here.
@admin.register(Challange)
class ChallangeAdmin(admin.ModelAdmin):
    ''' Define admin panel for action model '''
    list_display = ['pk', 'from_player', 'to_player', 'status']


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    ''' Define admin panel for action model '''
    list_display = ['pk', 'user']

