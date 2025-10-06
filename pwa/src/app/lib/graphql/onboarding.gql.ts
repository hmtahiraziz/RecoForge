import { gql } from '@apollo/client';

export interface EnquiryMutationResponse {
  id: string;
  firstName: string;
  surname: string;
  email: string;
  contactNumber: string;
  tradingName: string;
  entityType: string;
  outletType: string;
  cuisine: string;
  outletStyle: string;
  __typename: string;
}

export const CREATE_ENQUIRY = gql`
  mutation createEnquiry($input: EnquiryInput!) {
    createEnquiry(input: $input) {
      id
      firstName
      surname
      email
      contactNumber
      tradingName
      entityType
      outletType
      cuisine
      outletStyle
    }
  }
`;

export const UPDATE_ENQUIRY = gql`
  mutation updateEnquiry($id: String!, $input: EnquiryUpdateInput!) {
    updateEnquiry(id: $id, input: $input) {
      id
      firstName
      surname
      email
      contactNumber
      tradingName
      entityType
      outletType
      cuisine
      outletStyle
    }
  }
`;
