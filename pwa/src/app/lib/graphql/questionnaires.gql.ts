import { gql } from '@apollo/client';

export const GET_QUESTIONNAIRES = gql`
  query GetQuestionnaires {
    questionnaires {
      id
      categoryCode
      title
      description
      status
      isActive
      version
      createdAt
      updatedAt
      publishedAt
    }
  }
`;

export const CREATE_QUESTIONNAIRE = gql`
  mutation CreateQuestionnaire($input: QuestionnaireInput!) {
    createQuestionnaire(input: $input) {
      id
      categoryCode
      title
      description
      status
      isActive
      version
      createdAt
    }
  }
`;

export const UPDATE_QUESTIONNAIRE = gql`
  mutation UpdateQuestionnaire($id: String!, $input: QuestionnaireUpdateInput!) {
    updateQuestionnaire(id: $id, input: $input) {
      id
      categoryCode
      title
      description
      status
      isActive
      version
      updatedAt
    }
  }
`;

export const DELETE_QUESTIONNAIRE = gql`
  mutation DeleteQuestionnaire($id: String!) {
    deleteQuestionnaire(id: $id)
  }
`;

export const GET_QUESTIONNAIRE = gql`
  query GetQuestionnaire($id: String!) {
    questionnaire(id: $id) {
      id
      categoryCode
      title
      description
      status
      isActive
      version
      createdAt
      updatedAt
      questions {
        id
        key
        type
        label
        required
        orderIndex
        options {
          id
          value
          label
          orderIndex
        }
      }
    }
  }
`;

export const PUBLISH_QUESTIONNAIRE = gql`
  mutation PublishQuestionnaire($id: String!) {
    publishQuestionnaire(id: $id) {
      id
      categoryCode
      title
      description
      status
      isActive
      version
      publishedAt
    }
  }
`;

export const GET_QUESTIONNAIRE_BY_CATEGORY = gql`
  query getQuestionnaireByCategory($category: String!) {
    questionnaires(category: $category) {
      id
      title
      categoryCode
      status
      questions {
        id
        label
        type
        options {
          id
          value
          label
        }
      }
    }
  }
`;
