/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-nocheck

'use client';

import type { AdditionalDetailsFormProps, onSubmitHandlerProps } from './AdditionalDetailsForm.types';

import { useForm } from 'react-hook-form';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';

import { OUTLET_DESCRIPTION_OPTIONS, OUTLET_STYLE_OPTIONS } from './additionalDetailsForm.const';

import { UPDATE_ENQUIRY } from '@/app/lib/graphql/onboarding.gql';
import { apolloClient } from '@/app/lib/graphql/apolloClient';

const additionalDetailsFormSchema = yup.object().shape({
  venueTradingName: yup
    .string()
    .typeError('Venue trading name must be a string.')
    .required('Venue trading name is required.'),
  entityType: yup.string().required('Entity type is required.'),
  outletType: yup.string().required('Outlet type is required.'),
  outletStyle: yup.string().required('Outlet style is required.'),
  outletDescription: yup.string().when('outletType', ([outletType], schema) => {
    if (OUTLET_DESCRIPTION_OPTIONS[outletType as keyof typeof OUTLET_DESCRIPTION_OPTIONS]) {
      return schema.required('Outlet description is required.');
    }

    return schema.notRequired();
  })
});

const useAdditionalDetailsForm = ({ registration, setRegistration, setActiveStep }: AdditionalDetailsFormProps) => {
  const form = useForm({
    resolver: yupResolver(additionalDetailsFormSchema),
    defaultValues: {
      venueTradingName: registration.tradingName,
      entityType: '',
      outletType: '',
      outletStyle: '',
      outletDescription: ''
    }
  });

  const onSubmitHandler = async (data: onSubmitHandlerProps) => {
    const { id, ...restOfRegistration } = registration;

    const response = await apolloClient.mutate({
      mutation: UPDATE_ENQUIRY,
      variables: {
        id: id,
        input: {
          ...restOfRegistration,
          entityType: data.entityType ?? '',
          outletType: data.outletType ?? '',
          cuisine: data.outletDescription ?? '',
          outletStyle: data.outletStyle ?? '',
          productCategory: '',
          venueType: ''
        }
      }
    });

    const registrationData = response.data.updateEnquiry;

    delete registrationData.__typename;

    setRegistration(registrationData);
    setActiveStep(3);
  };

  const handleOutletTypeChange = () => {
    form.clearErrors('outletDescription');
    form.clearErrors('outletStyle');
    form.setValue('outletStyle', '');
    form.setValue('outletDescription', '');
  };

  const returnOutletStyleOptions = () => {
    return OUTLET_STYLE_OPTIONS[form.watch('outletType') as keyof typeof OUTLET_STYLE_OPTIONS] || [];
  };

  const returnOutletDescriptionOptions = () => {
    return OUTLET_DESCRIPTION_OPTIONS[form.watch('outletType') as keyof typeof OUTLET_DESCRIPTION_OPTIONS] || [];
  };

  const { outletType } = form.watch();
  const OutletDescriptionOptions = returnOutletDescriptionOptions();
  const OutletStyleOptions = returnOutletStyleOptions();

  return {
    form,
    handleSubmit: form.handleSubmit(onSubmitHandler),
    handleOutletTypeChange,
    isCreateOrUpdateLoading: false,
    OutletDescriptionOptions,
    OutletStyleOptions,
    outletType
  };
};

export default useAdditionalDetailsForm;
