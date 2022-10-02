import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
import graphql_jwt
from graphql_jwt.decorators import login_required
from sesame.utils import get_token


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username']


class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    me = graphene.String()

    @login_required
    def resolve_all_users(root, info):
        return get_user_model().objects.all()

    def resolve_me(root, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication credentials were not provided")
        token = get_token(user)
        return token


class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)