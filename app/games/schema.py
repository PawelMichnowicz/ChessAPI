import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model

from games.models import Challange, Player


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


class ChallangeInput(graphene.InputObjectType):
    player_id = graphene.ID()


class CreateChallange(graphene.Mutation):
    class Arguments:
        challange_data = ChallangeInput(required=True)

    challange = graphene.Field(ChallangeType)

    @staticmethod
    def mutate(root, info, challange_data=None):
        from_player = info.context.user.player
        to_player = get_user_model().objects.get(id=challange_data.player_id).player
        challange_instance = Challange(
            from_player=from_player, to_player=to_player)
        challange_instance.save()
        return CreateChallange(challange=challange_instance)


class Mutation(graphene.ObjectType):
    create_challange = CreateChallange.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
