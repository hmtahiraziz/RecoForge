'use client';

import type { BasicDetailsFormProps } from './BasicDetailsForm.types';

import React from 'react';
import { Controller } from 'react-hook-form';
import useBasicDetailsForm from './useBasicDetailsForm';
import { replaceNonNumeric } from '@/app/lib/utils/replaceNonNumeric';

import { getMaskedPhone } from '@/app/lib/utils/getMaskedPhone';
import { PLButton } from '@/app/components/ui/PL/PLButton/PLButton';
import {
  PLFormFieldControl,
  PLFormFieldError,
  PLFormFieldLabel,
  PLFormFieldRoot
} from '@/app/components/ui/PL/PLFormField';
import { PLInput } from '@/app/components/ui/PL/PLInput';

/** @param {BasicDetailsFormProps} props */
function BasicDetailsForm({ registration, setActiveStep, setRegistration }: BasicDetailsFormProps) {
  const { form, handleSubmit } = useBasicDetailsForm({
    registration,
    setActiveStep,
    setRegistration
  });

  return (
    <>
      <form
        id="customer-registration-form"
        className="flex flex-col gap-4 md:grid md:grid-cols-2 md:gap-6"
        onSubmit={handleSubmit}
      >
        <Controller
          control={form.control}
          name="firstName"
          render={({ field, fieldState }) => (
            <PLFormFieldRoot isInvalid={fieldState.invalid}>
              <PLFormFieldLabel>First name *</PLFormFieldLabel>
              <PLFormFieldControl>
                <PLInput
                  {...field}
                  disabled={form.formState.isSubmitting}
                  onChange={(event) => {
                    const newValue = event.target.value.replace(/[^a-zA-Z'\"\- ]/g, '');

                    field.onChange(newValue);
                  }}
                />
              </PLFormFieldControl>
              <PLFormFieldError>{fieldState.error?.message}</PLFormFieldError>
            </PLFormFieldRoot>
          )}
        />

        <Controller
          control={form.control}
          name="lastName"
          render={({ field, fieldState }) => (
            <PLFormFieldRoot isInvalid={fieldState.invalid}>
              <PLFormFieldLabel>Last name *</PLFormFieldLabel>
              <PLFormFieldControl>
                <PLInput
                  {...field}
                  disabled={form.formState.isSubmitting}
                  onChange={(event) => {
                    const newValue = event.target.value.replace(/[^a-zA-Z'\"\- ]/g, '');

                    field.onChange(newValue);
                  }}
                />
              </PLFormFieldControl>
              <PLFormFieldError>{fieldState.error?.message}</PLFormFieldError>
            </PLFormFieldRoot>
          )}
        />

        <Controller
          control={form.control}
          name="email"
          render={({ field, fieldState }) => (
            <PLFormFieldRoot isInvalid={fieldState.invalid}>
              <PLFormFieldLabel>Email *</PLFormFieldLabel>
              <PLFormFieldControl>
                <PLInput {...field} disabled={form.formState.isSubmitting} />
              </PLFormFieldControl>
              <PLFormFieldError>{fieldState.error?.message}</PLFormFieldError>
            </PLFormFieldRoot>
          )}
        />

        <Controller
          control={form.control}
          name="mobileNumber"
          render={({ field, fieldState }) => (
            <PLFormFieldRoot isInvalid={fieldState.invalid}>
              <PLFormFieldLabel>Mobile number *</PLFormFieldLabel>

              <PLFormFieldControl>
                <PLInput
                  {...field}
                  value={getMaskedPhone(field.value)}
                  disabled={form.formState.isSubmitting}
                  onChange={(event) => {
                    const newValue = replaceNonNumeric(event.target.value);
                    field.onChange(newValue);
                  }}
                />
              </PLFormFieldControl>
              <PLFormFieldError>{fieldState.error?.message}</PLFormFieldError>
            </PLFormFieldRoot>
          )}
        />

        <Controller
          control={form.control}
          name="venueTradingName"
          render={({ field, fieldState }) => (
            <PLFormFieldRoot className="col-span-2" isInvalid={fieldState.invalid}>
              <PLFormFieldLabel>Venue trading name *</PLFormFieldLabel>
              <PLFormFieldControl>
                <PLInput {...field} disabled={form.formState.isSubmitting} />
              </PLFormFieldControl>
              <PLFormFieldError>{fieldState.error?.message}</PLFormFieldError>
            </PLFormFieldRoot>
          )}
        />
      </form>

      <PLButton
        hierarchy="primary"
        disabled={form.formState.isSubmitting}
        form="customer-registration-form"
        className="mt-6 w-full md:ml-auto md:w-fit"
        type="submit"
        isLoading={form.formState.isSubmitting}
      >
        Next
      </PLButton>
    </>
  );
}

export default BasicDetailsForm;
