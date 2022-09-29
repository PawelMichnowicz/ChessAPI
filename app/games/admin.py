from django.contrib import admin
from .models import Duel

# Register your models here.
@admin.register(Duel)
class DuealAdmin(admin.ModelAdmin):
    ''' Define admin panel for action model '''
    list_display = ['pk', 'white_player', 'black_player']
