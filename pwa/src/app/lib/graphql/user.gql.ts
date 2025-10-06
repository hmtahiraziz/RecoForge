import { gql } from '@apollo/client';

export const GET_LOGIN_DETAILS = gql`
  mutation getUserDetails($email: String!, $password: String!) {
    loginAdminUser(loginInput: { email: $email, password: $password }) {
      accessToken
      adminUser {
        email
        id
        role
      }
    }
  }
`;
