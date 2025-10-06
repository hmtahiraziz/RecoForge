/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-nocheck

'use client';

import React, { useState } from 'react';
import BasicDetailsForm from '../BasicDetailsForm';
import { PWSteps } from '@/app/components/ui/PW/PWSteps';
import AdditionalDetailsForm from '../AdditionalDetailsForm';
import LaunchpadForm from '../LaunchpadForm';

export const FormContainer = () => {
  const [activeStep, setActiveStep] = useState(1);
  const [registration, setRegistration] = useState({
    success: false,
    entityId: 0,
    firstName: '',
    surname: '',
    email: '',
    contactNumber: '',
    venueTradingName: '',
    entityType: '',
    outletType: '',
    outletStyle: '',
    outletDescription: '',
    lastName: ''
  });

  const returnRegistrationStep: Record<number, React.ReactElement | null> = {
    1: <BasicDetailsForm setActiveStep={setActiveStep} registration={registration} setRegistration={setRegistration} />,
    2: (
      <AdditionalDetailsForm
        setActiveStep={setActiveStep}
        registration={registration}
        setRegistration={setRegistration}
      />
    ),
    3: <LaunchpadForm setActiveStep={setActiveStep} registration={registration} setRegistration={setRegistration} />
  };

  return (
    <div className="flex flex-col gap-6">
      <PWSteps.Root step={activeStep}>
        <PWSteps.Item index={1}>1</PWSteps.Item>
        <PWSteps.Item index={2}>2</PWSteps.Item>
        <PWSteps.Item index={3}>3</PWSteps.Item>
      </PWSteps.Root>
      <div className="flex w-full flex-col">
        <h1 className="text-heading-h1 mb-10 text-textcolor-primary">
          Become a <span className="text-textcolor-action">customer</span>
        </h1>

        {returnRegistrationStep[activeStep]}
      </div>
    </div>
  );
};
