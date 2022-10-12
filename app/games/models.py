from enum import Enum
from django.db import models
from django.contrib.auth import get_user_model
import uuid

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]

class StatusChoice(models.TextChoices):
    WAITING = 'waiting', 'Waiting'
    IN_GAME = 'in_game', "In game"
    DONE = 'done', 'Done'


class Player(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    username = models.CharField(max_length=25)


class Game(models.Model):
    is_draw = models.BooleanField(default=False)
    winner = models.ForeignKey(Player, related_name='winner', on_delete=models.SET(get_sentinel_user))
    loser = models.ForeignKey(Player, related_name='loser', on_delete=models.SET(get_sentinel_user))


class Challange(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=25, choices=StatusChoice.choices, default=StatusChoice.WAITING)
    from_player = models.ForeignKey(Player, related_name='my_challenges', on_delete=models.SET(get_sentinel_user))
    to_player = models.ForeignKey(Player, related_name='challanges', on_delete=models.SET(get_sentinel_user))
    game = models.OneToOneField(Game, null=True, blank=True, default=None, related_name='game', on_delete=models.SET_NULL)
    # game = Game(default=None, constraints only Done have a dame)



# class Duel(models.Model):
#     white_player = models.ForeignKey(get_user_model(), related_name='matches_white', on_delete=models.CASCADE)
#     black_player = models.ForeignKey(get_user_model(), related_name='mathess_black', on_delete=models.CASCADE)
