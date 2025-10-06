export type Registration = {
  id: number | null;
  contactNumber: string;
  cuisine: string | null;
  email: string;
  entityType: string;
  firstName: string;
  outletStyle: string;
  outletType: string;
  surname: string;
  tradingName: string;
};

export type BasicDetailsFormProps = {
  setActiveStep: (step: number) => void;
  registration: Registration;
  setRegistration: (registration: Registration) => void;
};

export type UseBasicDetailsFormProps = BasicDetailsFormProps;

export type onSubmitHandlerProps = {
  firstName: string;
  lastName: string;
  email: string;
  mobileNumber: string;
  venueTradingName: string;
  outletDescription: string;
};
