import { ApolloClient, InMemoryCache, HttpLink, from } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { retrieveCookie } from '../../actions/cookies/cookies';

const httpLink = new HttpLink({
  uri: 'http://localhost:8000/graphql'
});

const authLink = setContext(async (_, { headers }) => {
  // Get the authentication token from cookies
  const user = await retrieveCookie('user');
  const token = user?.token;

  // Return the headers to the context so httpLink can read them
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : ''
    }
  };
});

export const apolloClient = new ApolloClient({
  link: from([authLink, httpLink]),
  cache: new InMemoryCache()
});
