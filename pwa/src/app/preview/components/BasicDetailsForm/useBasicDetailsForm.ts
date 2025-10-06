/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-nocheck

'use client';

import type { UseBasicDetailsFormProps, onSubmitHandlerProps } from './BasicDetailsForm.types';

import { useForm } from 'react-hook-form';

import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';
import { apolloClient } from '@/app/lib/graphql/apolloClient';
import { CREATE_ENQUIRY, UPDATE_ENQUIRY } from '@/app/lib/graphql/onboarding.gql';

export const numbersOnlyRegex = /^[0-9]+$/;

const basicDetailsFormSchema = yup.object().shape({
  firstName: yup.string().typeError('First name must be a string.').required('First name is required.'),
  lastName: yup.string().typeError('Last name must be a string.').required('Last name is required.'),
  email: yup.string().email('Invalid email').required('Email is required.'),
  mobileNumber: yup
    .string()
    .transform((value) => {
      return value.replace(/\s/g, '');
    })
    .required('Mobile number is required.')
    .matches(numbersOnlyRegex, 'Mobile number must contain only numbers.')
    .min(10, 'Mobile number must be 10 digits.')
    .max(10, 'Mobile number must be 10 digits.'),
  venueTradingName: yup
    .string()
    .typeError('Venue trading name must be a string.')
    .required('Venue trading name is required.')
});

function useBasicDetailsForm({ registration, setActiveStep, setRegistration }: UseBasicDetailsFormProps) {
  const form = useForm({
    resolver: yupResolver(basicDetailsFormSchema),
    defaultValues: returnInitialValues()
  });

  function returnInitialValues() {
    return registration.firstName
      ? {
          firstName: registration.firstName,
          lastName: registration.surname,
          email: registration.email,
          mobileNumber: registration.contactNumber,
          venueTradingName: registration.tradingName
        }
      : {
          firstName: '',
          lastName: '',
          email: '',
          mobileNumber: '',
          venueTradingName: ''
        };
  }

  const onSubmitHandler = async (data: onSubmitHandlerProps) => {
    if (!registration.id) {
      const response = await apolloClient.mutate({
        mutation: CREATE_ENQUIRY,
        variables: {
          input: {
            firstName: data.firstName,
            surname: data.lastName,
            email: data.email,
            contactNumber: data.mobileNumber,
            tradingName: data.venueTradingName,
            entityType: '',
            outletType: '',
            cuisine: '',
            outletStyle: '',
            productCategory: '',
            venueType: ''
          }
        }
      });

      const registrationData = response.data.createEnquiry;

      delete registrationData.__typename;

      setRegistration(registrationData);
      setActiveStep(2);
    } else {
      const response = await apolloClient.mutate({
        mutation: UPDATE_ENQUIRY,
        variables: {
          id: registration.id,
          input: {
            firstName: data.firstName,
            surname: data.lastName,
            email: data.email,
            contactNumber: data.mobileNumber,
            tradingName: data.venueTradingName,
            entityType: registration.entityType ?? '',
            outletType: registration.outletType ?? '',
            cuisine: registration.cuisine ?? '',
            outletStyle: registration.outletStyle ?? '',
            productCategory: '',
            venueType: registration.venueType ?? ''
          }
        }
      });

      const registrationData = response.data.updateEnquiry;

      delete registrationData.__typename;

      setRegistration(registrationData);
      setActiveStep(2);
    }
  };

  return {
    form,
    handleSubmit: form.handleSubmit(onSubmitHandler)
  };
}

export default useBasicDetailsForm;
