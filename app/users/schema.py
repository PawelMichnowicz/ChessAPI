import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
import graphql_jwt
from graphql_jwt.decorators import login_required
from sesame.utils import get_token


class UserType(DjangoObjectType):
    """
    GraphQL type representing the User model.

    Fields:
        id (ID): The unique identifier of the user.
        username (String): The username of the user.
    """
    class Meta:
        model = get_user_model()
        fields = ['id', 'username']


class Query(graphene.ObjectType):
    """
    GraphQL query class.

    Provides the following queries:
        - all_users: Fetches a list of all users.
        - me: Fetches the current authenticated user's token.
    """
    all_users = graphene.List(UserType)
    me = graphene.String()

    @login_required
    def resolve_all_users(root, info):
        """
        Fetch and return a list of all users.
        """
        return get_user_model().objects.all()

    def resolve_me(root, info):
        """
        Fetch and return the token of the current authenticated user.

        Returns:
            str: The token of the current authenticated user.

        Raises:
            Exception: If authentication credentials were not provided.
        """
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication credentials were not provided")
        token = get_token(user)
        return token


class Mutation(graphene.ObjectType):
    """
    GraphQL mutation class.

    Note:
        The mutations are provided by the 'graphql_jwt' package.
    """

    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)