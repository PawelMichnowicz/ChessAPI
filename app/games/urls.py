from django.urls import path
from games.schema import schema
from graphene_django.views import GraphQLView
from graphql_jwt.decorators import jwt_cookie

urlpatterns = [
    path("graphql/", jwt_cookie(GraphQLView.as_view(graphiql=True, schema=schema))),
]
