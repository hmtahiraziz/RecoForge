import { Registration } from '../BasicDetailsForm/BasicDetailsForm.types';

export type AdditionalDetailsFormProps = {
  setActiveStep: (step: number) => void;
  registration: Registration;
  setRegistration: (registration: Registration) => void;
};

export type onSubmitHandlerProps = {
  entityType: string;
  outletDescription: string;
  outletStyle: string;
  outletType: string;
  venueTradingName: string;
};
