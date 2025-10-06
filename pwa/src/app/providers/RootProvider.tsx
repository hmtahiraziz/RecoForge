'use client';

import React from 'react';

import { ApolloProvider } from '@apollo/client/react';
import { apolloClient } from '@/app/lib/graphql/apolloClient';
import { UserContextProvider } from './UserContextProvider';

export const RootProvider = ({ children }: { children: React.ReactNode }) => {
  return (
    <ApolloProvider client={apolloClient}>
      <UserContextProvider>{children}</UserContextProvider>
    </ApolloProvider>
  );
};
