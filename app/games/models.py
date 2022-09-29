from django.db import models
from django.contrib.auth import get_user_model


# class Challange(models.Model):
#     status = None
#     from_player = None # player
#     to_player = None # player


# class Player(models.Model):
#     user = None #One to one


class Duel(models.Model):
    white_player = models.ForeignKey(get_user_model(), related_name='matches_white', on_delete=models.CASCADE)
    black_player = models.ForeignKey(get_user_model(), related_name='mathess_black', on_delete=models.CASCADE)
