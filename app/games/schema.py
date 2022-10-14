import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model

from games.models import Challange, Game, StatusChoice


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ["username", 'id']


class ChallangeType(DjangoObjectType):
    class Meta:
        model = Challange
        fields = "__all__"

    user = graphene.Field(UserType)


class Query(graphene.ObjectType):
    challange = graphene.Field(
        ChallangeType,
        game_id=graphene.String()
    )

    def resolve_challange(root, info, game_id):
        return Challange.objects.filter(id=game_id).first()


# class ChallangeInput(graphene.InputObjectType):
#     player_id = graphene.ID()


class CreateChallange(graphene.Mutation):
    class Arguments:
        # challange_data = ChallangeInput(required=True) #nested
        user_id = graphene.ID()

    challange = graphene.Field(ChallangeType)

    @staticmethod
    def mutate(root, info, user_id=None):
        from_user = info.context.user
        to_user = get_user_model().objects.get(id=user_id)
        challange_instance = Challange(
            from_user=from_user, to_user=to_user)
        challange_instance.save()
        return CreateChallange(challange=challange_instance)


class GameType(DjangoObjectType):
    class Meta:
        model = Challange
        fields = "__all__"


class EndGame(graphene.Mutation):
    class Arguments:
        challange_id = graphene.ID()
        winner_username = graphene.String()

    challange = graphene.Field(ChallangeType)

    @staticmethod
    def mutate(root, info, challange_id, winner_username):
        challange = Challange.objects.get(id=challange_id)
        if winner_username:
            winner = get_user_model().objects.get(username=winner_username)
            if challange.from_user == winner:
                loser = challange.to_user
            else:
                loser = challange.from_user
            game = Game(winner=winner, loser=loser)
            winner.elo_rating = winner.updated_elo(loser, 1)
            loser.elo_rating = loser.updated_elo(winner, 0)
            winner.save()
            loser.save()
        else: # If they played a draw
            game = Game(is_draw=True)
            challange.from_user.elo_rating = challange.from_user.updated_elo(challange.to_user, 0.5)
            challange.to_user.elo_rating = challange.to_user.updated_elo(challange.from_user, 0.5)
            challange.from_user.save()
            challange.to_user.save()

        game.save()
        challange.game = game
        challange.status = StatusChoice.DONE
        challange.save()
        return CreateChallange(challange=challange)


class Mutation(graphene.ObjectType):
    create_challange = CreateChallange.Field()
    end_game = EndGame.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
