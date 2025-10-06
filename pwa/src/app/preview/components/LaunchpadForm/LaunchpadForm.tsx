/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-nocheck

'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { Controller } from 'react-hook-form';
import useLaunchpadForm from './useLaunchpadForm';

import { PLButton } from '@/app/components/ui/PL/PLButton/PLButton';
import {
  PLFormFieldControl,
  PLFormFieldError,
  PLFormFieldLabel,
  PLFormFieldRoot
} from '@/app/components/ui/PL/PLFormField';
import { PLRadioGroupRoot, PLRadioGroupItem, PLRadioGroupItemLabel } from '@/app/components/ui/PL/PLRadioGroup';
import { DynamicQuestion } from './LaunchpadForm.types';
import { GET_QUESTIONNAIRE_BY_CATEGORY } from '@/app/lib/graphql/questionnaires.gql';
import { apolloClient } from '@/app/lib/graphql/apolloClient';
import RecommendationsModal from './RecommendationsModal';

function QuestionRenderer({
  question,
  control,
  formState
}: {
  question: DynamicQuestion;
  control: any;
  formState: any;
}) {
  return (
    <Controller
      key={question.id}
      control={control}
      name={question.id}
      render={({ field, fieldState }) => (
        <PLFormFieldRoot isInvalid={fieldState.invalid}>
          <PLFormFieldLabel>{question.label} *</PLFormFieldLabel>
          {question.type === 'SINGLE' ? (
            <PLFormFieldControl>
              <PLRadioGroupRoot value={field.value} onValueChange={field.onChange} disabled={formState.isSubmitting}>
                {question.options.map((option) => (
                  <div key={option.id} className="flex items-center space-x-2">
                    <PLRadioGroupItem value={option.value} id={option.id} />
                    <PLRadioGroupItemLabel htmlFor={option.id}>{option.label}</PLRadioGroupItemLabel>
                  </div>
                ))}
              </PLRadioGroupRoot>
            </PLFormFieldControl>
          ) : question.type === 'MULTI' ? (
            <div className="space-y-2">
              {question.options.map((option) => (
                <div key={option.id} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id={option.id}
                    value={option.value}
                    checked={field.value?.includes(option.value) || false}
                    onChange={(event) => {
                      const currentValues = field.value || [];
                      if (event.target.checked) {
                        field.onChange([...currentValues, option.value]);
                      } else {
                        field.onChange(currentValues.filter((value: string) => value !== option.value));
                      }
                    }}
                    disabled={formState.isSubmitting}
                    className="rounded border-gray-300"
                  />
                  <label htmlFor={option.id} className="text-sm font-medium">
                    {option.label}
                  </label>
                </div>
              ))}
            </div>
          ) : null}

          <PLFormFieldError>{fieldState.error?.message}</PLFormFieldError>
        </PLFormFieldRoot>
      )}
    />
  );
}

function LaunchpadForm({
  registration,
  setActiveStep
}: {
  registration: Registration;
  setActiveStep: (step: number) => void;
}) {
  const [questions, setQuestions] = useState<DynamicQuestion[]>([]);
  const [loading, setLoading] = useState(false);

  const { form, handleSubmit, isModalOpen, setIsModalOpen, recommendations, isLoading } = useLaunchpadForm({
    registration,
    questions
  });

  const loadQuestions = useCallback(async () => {
    setLoading(true);

    const response = await apolloClient.query({
      query: GET_QUESTIONNAIRE_BY_CATEGORY,
      variables: { category: registration.outletType }
    });
    const questions = response.data.questionnaires[0].questions;

    setQuestions(questions);

    setLoading(false);
  }, [registration.outletType]);

  useEffect(() => {
    loadQuestions();
  }, [loadQuestions]);

  return loading ? (
    <span>Loading...</span>
  ) : (
    <>
      <form
        id="customer-registration-form"
        className="flex flex-col gap-4 md:grid md:grid-cols-2 md:gap-6"
        onSubmit={handleSubmit}
      >
        {questions.map((question) => (
          <QuestionRenderer key={question.id} question={question} control={form.control} formState={form.formState} />
        ))}
      </form>

      <div className="mt-6 flex w-full gap-4 md:ml-auto md:w-fit">
        <PLButton
          disabled={form.formState.isSubmitting}
          hierarchy="secondary"
          onClick={() => setActiveStep(2)}
          className="w-full md:w-fit"
        >
          Back
        </PLButton>
        <PLButton
          disabled={form.formState.isSubmitting || isLoading}
          type="submit"
          form="customer-registration-form"
          hierarchy="primary"
          className="w-full md:ml-auto md:w-fit"
          isLoading={form.formState.isSubmitting || isLoading}
        >
          {isLoading ? 'Getting Recommendations...' : 'Get Recommendations'}
        </PLButton>
      </div>

      {/* Recommendations Modal */}
      {recommendations && (
        <RecommendationsModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          recommendations={recommendations.items || []}
          query={recommendations.query || 'Drinks'}
          confidence={recommendations.confidence || 0}
          totalItems={recommendations.total_items || 0}
          processingTimeMs={recommendations.processing_time_ms || 0}
        />
      )}
    </>
  );
}

export default LaunchpadForm;
