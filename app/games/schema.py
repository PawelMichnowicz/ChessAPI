import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model

from games.models import Challange, Player, Game, StatusChoice

class PlayerType(DjangoObjectType):
    class Meta:
        model = Player
        fields = ["username", 'id']


class ChallangeType(DjangoObjectType):
    class Meta:
        model = Challange
        fields = "__all__"

    player = graphene.Field(PlayerType)


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
        player_id = graphene.ID()

    challange = graphene.Field(ChallangeType)

    @staticmethod
    def mutate(root, info, player_id=None):
        from_player = info.context.user.player
        to_player = get_user_model().objects.get(id=player_id).player
        challange_instance = Challange(
            from_player=from_player, to_player=to_player)
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
            winner = get_user_model().objects.get(username=winner_username).player
            if challange.from_player == winner:
                loser = challange.to_player
            else:
                loser = challange.from_player
            game = Game(winner=winner, loser=loser)
        else:
            game = Game(is_draw=True)
        game.save()
        challange.game = game
        challange.status = StatusChoice.DONE
        challange.save()
        return CreateChallange(challange=challange)


class Mutation(graphene.ObjectType):
    create_challange = CreateChallange.Field()
    end_game = EndGame.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
