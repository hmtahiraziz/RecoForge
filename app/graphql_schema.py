import strawberry
from graphql_resolvers import Query, Mutation

# Create the GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)
