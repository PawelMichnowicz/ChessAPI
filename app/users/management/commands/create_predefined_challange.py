from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from games.models import Challange

CHALLANGE_ID_PREDEFINED = "12341234-1234-1234-1234-aaaaaaaaaaaa"
PLAYER_1 = "player_1"
PLAYER_2 = "player_2"
PASSWORD = "123"

class Command(BaseCommand):
    """Django command to create predefined users"""

    def handle(self, *args, **options):
        """Entrypoint for command"""
        if not get_user_model().objects.filter(username=PLAYER_1).exists():
            player_1 = get_user_model().objects.create_user(PLAYER_1, PASSWORD)
        else:
            player_1 = get_user_model().objects.get(username=PLAYER_1)

        if not get_user_model().objects.filter(username=PLAYER_2).exists():
            player_2 = get_user_model().objects.create_user(PLAYER_2, PASSWORD)
        else:
            player_2 = get_user_model().objects.get(username=PLAYER_2)

        if not Challange.objects.filter(id=CHALLANGE_ID_PREDEFINED).exists():
            Challange.objects.create(from_user=player_1, to_user=player_2, id=CHALLANGE_ID_PREDEFINED)
