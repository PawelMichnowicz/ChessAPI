import math
import uuid

from django.contrib.auth import get_user_model
from django.db import models


ELO_START_VALUE = 400
ELO_FACTOR_K = 20


def get_or_create_deleted_user_instance():
    """
    Creates or retrieves a special 'deleted' user.

    Returns:
        User: The 'deleted' user instance.
    """
    return get_user_model().objects.get_or_create(username="deleted")[0]


class StatusChoice(models.TextChoices):
    """
    A choices class representing the possible status values for a Challange.

    Attributes:
        WAITING (str): The Challange is waiting for a response.
        IN_GAME (str): The Challange is in progress and a game has started.
        DONE (str): The Challange is completed.
    """

    WAITING = "waiting", "Waiting"
    IN_GAME = "in_game", "In game"
    DONE = "done", "Done"


class Game(models.Model):
    """
    Represents a game played between two users.

    Attributes:
        is_draw (bool): Indicates if the game ended in a draw.
        winner (User): The User who won the game, or None if the game ended in a draw.
        loser (User): The User who lost the game, or None if the game ended in a draw.
    """

    is_draw = models.BooleanField(default=False)
    winner = models.ForeignKey(
        get_user_model(),
        null=True,
        related_name="winner",
        on_delete=models.SET(get_or_create_deleted_user_instance),
    )
    loser = models.ForeignKey(
        get_user_model(),
        null=True,
        related_name="loser",
        on_delete=models.SET(get_or_create_deleted_user_instance),
    )


class Challange(models.Model):
    """
    Represents a challenge from one user to another for a game.

    Attributes:
        id (UUIDField): A unique identifier for the challenge.
        status (StatusChoice): The current status of the challenge.
        from_user (User): The User who sent the challenge.
        to_user (User): The User who received the challenge.
        game (Game): The associated Game instance.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=25, choices=StatusChoice.choices, default=StatusChoice.WAITING
    )
    from_user = models.ForeignKey(
        get_user_model(),
        related_name="my_challenges",
        on_delete=models.SET(get_or_create_deleted_user_instance),
    )
    to_user = models.ForeignKey(
        get_user_model(),
        related_name="challanges",
        on_delete=models.SET(get_or_create_deleted_user_instance),
    )
    game = models.OneToOneField(
        Game,
        null=True,
        blank=True,
        default=None,
        related_name="game",
        on_delete=models.SET_NULL,
    )

    def calculate_elo_rating(self, player, opponent, result):
        """
        Calculate the updated Elo rating of a player after a game.

        Args:
            player (User): The User who played the game.
            opponent (User): The User who played against the player.
            result (float): The result of the game (1.0-win, 0.5-draw, 0.0-loss).

        Returns:
            float: The updated Elo rating of the player after the game.
        """
        probability = 1 / (
            1
            + math.pow(10, (opponent.elo_rating - player.elo_rating) / ELO_START_VALUE)
        )
        return round(player.elo_rating + ELO_FACTOR_K * (result - probability), 1)
