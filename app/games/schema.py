import graphene
from graphene_django import DjangoObjectType
from graphene.types.json import JSONString
from django.contrib.auth import get_user_model

from games.models import Challange, Game, StatusChoice


class UserType(DjangoObjectType):
    """
    Represents a user in the system.
    """

    class Meta:
        model = get_user_model()
        fields = ["username", "elo_rating", "id"]


class ChallangeType(DjangoObjectType):
    """
    Represents a challenge between two users.

    Fields:
        user (UserType): The user who sent the challenge.
        elo_rating_changes (JSONString): The Elo rating possibilities for each user after the challenge.
    """

    user = graphene.Field(UserType)
    elo_rating_changes = graphene.Field(JSONString)

    class Meta:
        model = Challange
        fields = "__all__"

    def resolve_elo_rating_changes(self, info):
        """
        Calculate the possible Elo rating that will be assigned to the playe after the challenge, depending on the result.

        Returns:
            dict: A dictionary contains possible Elo ratings
        """
        elo_rating_dict = {
            self.from_user.username: {
                "win": self.calculate_elo_rating(self.from_user, self.to_user, 1),
                "draw": self.calculate_elo_rating(self.from_user, self.to_user, 0.5),
                "lose": self.calculate_elo_rating(self.from_user, self.to_user, 0),
            },
            self.to_user.username: {
                "win": self.calculate_elo_rating(self.to_user, self.from_user, 1),
                "draw": self.calculate_elo_rating(self.to_user, self.from_user, 0.5),
                "lose": self.calculate_elo_rating(self.to_user, self.from_user, 0),
            },
        }
        return elo_rating_dict


class Query(graphene.ObjectType):
    """
    The root query for GraphQL.

    Fields:
        challange (ChallangeType): Query to fetch a challenge by its game_id.
    """
    challange = graphene.Field(ChallangeType, game_id=graphene.String())

    def resolve_challange(root, info, game_id):
        """
        Resolve the challenge by its game_id.

        Args:
            game_id (str): The unique identifier of the challenge.
        """
        return Challange.objects.filter(id=game_id).first()


class CreateChallange(graphene.Mutation):
    """
    Mutation to create a new challenge between users.

    Arguments:
        user_id (ID): The ID of the user who receives the challenge.
    """
    class Arguments:
        user_id = graphene.ID()

    challange = graphene.Field(ChallangeType)

    @staticmethod
    def mutate(root, info, user_id=None):
        """
        Mutate to create a new challenge between users.
        """
        from_user = info.context.user
        to_user = get_user_model().objects.get(id=user_id)
        challange_instance = Challange(from_user=from_user, to_user=to_user)
        challange_instance.save()
        return CreateChallange(challange=challange_instance)


class GameType(DjangoObjectType):
    """
    Represents a game played between two users.
    """
    class Meta:
        model = Challange
        fields = "__all__"


class EndGame(graphene.Mutation):
    """
    Mutation to end a game and calculate the Elo rating changes for the players.

    Arguments:
        challange_id (ID): The ID of the challenge that corresponds to the game.
        winner_username (str): The username of the winner, or None for a draw.

    Fields:
        challange (ChallangeType): The updated challenge instance.
    """
    class Arguments:
        challange_id = graphene.ID()
        winner_username = graphene.String()

    challange = graphene.Field(ChallangeType)

    @staticmethod
    def mutate(root, info, challange_id, winner_username):
        """
        Mutate to end a game and calculate the Elo rating changes for the players.
        """
        challange = Challange.objects.get(id=challange_id)
        if winner_username:
            winner = get_user_model().objects.get(username=winner_username)
            if challange.from_user == winner:
                loser = challange.to_user
            else:
                loser = challange.from_user
            game = Game(winner=winner, loser=loser)
            winner.elo_rating = challange.calculate_elo_rating(winner, loser, 1)
            loser.elo_rating = challange.calculate_elo_rating(loser, winner, 0)
            winner.save()
            loser.save()
        else:  # If they played a draw
            game = Game(is_draw=True)
            challange.from_user.elo_rating = challange.calculate_elo_rating(
                challange.from_user, challange.to_user, 0.5
            )
            challange.to_user.elo_rating = challange.calculate_elo_rating(
                challange.to_user, challange.from_user, 0.5
            )
            challange.from_user.save()
            challange.to_user.save()

        game.save()
        challange.game = game
        challange.status = StatusChoice.DONE
        challange.save()
        return CreateChallange(challange=challange)


class Mutation(graphene.ObjectType):
    """
    The root mutation for GraphQL.
    """
    create_challange = CreateChallange.Field()
    end_game = EndGame.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
