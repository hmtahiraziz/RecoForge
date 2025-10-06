import { Registration } from '../BasicDetailsForm/BasicDetailsForm.types';

export type QuestionType = 'SINGLE' | 'MULTI';

export type QuestionOption = {
  id: string;
  label: string;
  value: string;
};

export type DynamicQuestion = {
  id: string;
  label: string;
  type: QuestionType;
  options: QuestionOption[];
};

export type Questionnaire = {
  id: string;
  title: string;
  categoryCode: string;
  status: string;
  questions: DynamicQuestion[];
};

export type QuestionnaireResponse = {
  data: {
    questionnaires: Questionnaire[];
  };
};

export type LaunchpadFormProps = {
  setActiveStep: (step: number) => void;
  registration: Registration;
};
