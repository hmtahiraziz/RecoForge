import { Controller } from 'react-hook-form';

import {
  PLFormFieldControl,
  PLFormFieldError,
  PLFormFieldLabel,
  PLFormFieldRoot
} from '@/app/components/ui/PL/PLFormField';

import { PLInput } from '@/app/components/ui/PL/PLInput';
import { PLButton } from '@/app/components/ui/PL/PLButton/PLButton';
import useAdditionalDetailsForm from './useAdditionalDetailsForm';

import { PLSelect } from '@/app/components/ui/PL/PLSelect';
import { ENTITY_TYPES, OUTLET_TYPE_OPTIONS } from './additionalDetailsForm.const';
import { AdditionalDetailsFormProps } from './AdditionalDetailsForm.types';

function AdditionalDetailsForm({ registration, setActiveStep, setRegistration }: AdditionalDetailsFormProps) {
  const { form, handleSubmit, handleOutletTypeChange, OutletDescriptionOptions, OutletStyleOptions, outletType } =
    useAdditionalDetailsForm({
      registration,
      setRegistration,
      setActiveStep
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
          name="venueTradingName"
          render={({ field, fieldState }) => (
            <PLFormFieldRoot isInvalid={fieldState.invalid}>
              <PLFormFieldLabel>Venue trading name *</PLFormFieldLabel>
              <PLFormFieldControl>
                <PLInput {...field} disabled />
              </PLFormFieldControl>
              <PLFormFieldError>{fieldState.error?.message}</PLFormFieldError>
            </PLFormFieldRoot>
          )}
        />

        <Controller
          control={form.control}
          name="entityType"
          render={({ field, fieldState }) => (
            <PLFormFieldRoot isInvalid={fieldState.invalid}>
              <PLFormFieldLabel>Entity type *</PLFormFieldLabel>

              <PLSelect.Root
                value={field.value}
                disabled={form.formState.isSubmitting}
                onValueChange={(value) => {
                  field.onChange(value);
                }}
              >
                <PLFormFieldControl>
                  <PLSelect.Trigger placeholder={'Select...'} showExpandIcon={true} />
                </PLFormFieldControl>
                <PLSelect.Content>
                  {ENTITY_TYPES.map((item, index) => (
                    <PLSelect.MenuDefaultItem key={index} value={item.value}>
                      {item.value}
                    </PLSelect.MenuDefaultItem>
                  ))}
                </PLSelect.Content>
              </PLSelect.Root>

              <PLFormFieldError>{fieldState.error?.message}</PLFormFieldError>
            </PLFormFieldRoot>
          )}
        />

        <Controller
          control={form.control}
          name="outletType"
          render={({ field, fieldState }) => (
            <PLFormFieldRoot isInvalid={fieldState.invalid}>
              <PLFormFieldLabel>Outlet type *</PLFormFieldLabel>

              <PLSelect.Root
                disabled={form.formState.isSubmitting}
                value={field.value}
                onValueChange={(value) => {
                  handleOutletTypeChange();
                  field.onChange(value);
                }}
              >
                <PLFormFieldControl>
                  <PLSelect.Trigger placeholder={'Select...'} showExpandIcon={true} />
                </PLFormFieldControl>
                <PLSelect.Content>
                  {OUTLET_TYPE_OPTIONS.map((item, index) => (
                    <PLSelect.MenuDefaultItem key={index} value={item.value}>
                      {item.value}
                    </PLSelect.MenuDefaultItem>
                  ))}
                </PLSelect.Content>
              </PLSelect.Root>

              <PLFormFieldError>{fieldState.error?.message}</PLFormFieldError>
            </PLFormFieldRoot>
          )}
        />

        {outletType !== '' && (
          <Controller
            control={form.control}
            name="outletStyle"
            render={({ field, fieldState }) => (
              <PLFormFieldRoot isInvalid={fieldState.invalid}>
                <PLFormFieldLabel>Outlet style *</PLFormFieldLabel>

                <PLSelect.Root
                  value={field.value}
                  onValueChange={field.onChange}
                  disabled={form.formState.isSubmitting}
                >
                  <PLFormFieldControl>
                    <PLSelect.Trigger placeholder={'Select...'} showExpandIcon={true} />
                  </PLFormFieldControl>
                  <PLSelect.Content>
                    {OutletStyleOptions.map((item, index) => (
                      <PLSelect.MenuDefaultItem key={index} value={item.value}>
                        {item.value}
                      </PLSelect.MenuDefaultItem>
                    ))}
                  </PLSelect.Content>
                </PLSelect.Root>

                <PLFormFieldError>{fieldState.error?.message}</PLFormFieldError>
              </PLFormFieldRoot>
            )}
          />
        )}

        {OutletDescriptionOptions.length > 0 && (
          <Controller
            control={form.control}
            name="outletDescription"
            render={({ field, fieldState }) => (
              <PLFormFieldRoot isInvalid={fieldState.invalid}>
                <PLFormFieldLabel>Outlet description *</PLFormFieldLabel>

                <PLSelect.Root
                  value={field.value}
                  onValueChange={field.onChange}
                  disabled={form.formState.isSubmitting}
                >
                  <PLFormFieldControl>
                    <PLSelect.Trigger placeholder={'Select...'} showExpandIcon={true} />
                  </PLFormFieldControl>
                  <PLSelect.Content>
                    {OutletDescriptionOptions.map((item, index) => (
                      <PLSelect.MenuDefaultItem key={index} value={item.value}>
                        {item.value}
                      </PLSelect.MenuDefaultItem>
                    ))}
                  </PLSelect.Content>
                </PLSelect.Root>

                <PLFormFieldError>{fieldState.error?.message}</PLFormFieldError>
              </PLFormFieldRoot>
            )}
          />
        )}
      </form>

      <div className="mt-6 flex w-full gap-4 md:ml-auto md:w-fit">
        <PLButton
          disabled={form.formState.isSubmitting}
          hierarchy="secondary"
          onClick={() => setActiveStep(1)}
          className="w-full md:w-fit"
        >
          Back
        </PLButton>
        <PLButton
          disabled={form.formState.isSubmitting}
          type="submit"
          form="customer-registration-form"
          hierarchy="primary"
          className="w-full md:ml-auto md:w-fit"
          isLoading={form.formState.isSubmitting}
        >
          Next
        </PLButton>
      </div>
    </>
  );
}

export default AdditionalDetailsForm;
