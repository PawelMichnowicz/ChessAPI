import math
import uuid

from django.contrib.auth import get_user_model
from django.db import models


ELO_START_VALUE = 400
ELO_FACTOR_K = 20


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


class StatusChoice(models.TextChoices):
    WAITING = 'waiting', 'Waiting'
    IN_GAME = 'in_game', "In game"
    DONE = 'done', 'Done'


class Game(models.Model):
    is_draw = models.BooleanField(default=False)
    winner = models.ForeignKey(get_user_model(
    ), null=True, related_name='winner', on_delete=models.SET(get_sentinel_user))
    loser = models.ForeignKey(get_user_model(
    ), null=True, related_name='loser', on_delete=models.SET(get_sentinel_user))


class Challange(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=25, choices=StatusChoice.choices, default=StatusChoice.WAITING)
    from_user = models.ForeignKey(get_user_model(
    ), related_name='my_challenges', on_delete=models.SET(get_sentinel_user))
    to_user = models.ForeignKey(get_user_model(
    ), related_name='challanges', on_delete=models.SET(get_sentinel_user))
    game = models.OneToOneField(Game, null=True, blank=True,
                                default=None, related_name='game', on_delete=models.SET_NULL)


    def calculate_elo_rating(self, player, opponent, result):
        probability = 1 / (
            1 + math.pow(10, (opponent.elo_rating - player.elo_rating) / ELO_START_VALUE)
        )
        return round(player.elo_rating + ELO_FACTOR_K * (result - probability), 1)


