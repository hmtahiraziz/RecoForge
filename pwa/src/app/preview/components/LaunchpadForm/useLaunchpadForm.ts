'use client';

import { useForm } from 'react-hook-form';
import { useEffect, useState } from 'react';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';
import { DynamicQuestion } from './LaunchpadForm.types';
import { Registration } from '../BasicDetailsForm/BasicDetailsForm.types';

export const numbersOnlyRegex = /^[0-9]+$/;

function createDynamicSchema(questions: DynamicQuestion[]) {
  const schemaFields: Record<string, any> = {};

  questions.forEach((question) => {
    if (question.type === 'SINGLE') {
      schemaFields[question.id] = yup.string().required(`${question.label} is required.`);
    } else if (question.type === 'MULTI') {
      schemaFields[question.id] = yup
        .array()
        .of(yup.string())
        .min(1, `${question.label} requires at least one selection.`);
    }
  });

  return yup.object().shape(schemaFields);
}

function useLaunchpadForm({ questions, registration }: { questions: DynamicQuestion[]; registration: Registration }) {
  const dynamicSchema = createDynamicSchema(questions);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm({
    resolver: yupResolver(dynamicSchema),
    defaultValues: {}
  });

  // Reset form when questions change
  useEffect(() => {
    if (questions.length > 0) {
      const defaultValues: Record<string, any> = {};
      questions.forEach((question) => {
        if (question.type === 'MULTI') {
          defaultValues[question.id] = [];
        } else {
          defaultValues[question.id] = '';
        }
      });
      form.reset(defaultValues);
    }
  }, [questions, form]);

  const onSubmitHandler = async () => {
    try {
      setIsLoading(true);
      console.log('Sending request with data:', {
        query: 'Drinks',
        answers: {
          categories: [registration.outletStyle, registration.cuisine]
        },
        limit: 10
      });

      const response = await fetch('http://localhost:8000/recs/recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: 'Drinks',
          answers: {
            categories: [registration.outletStyle, registration.cuisine]
          },
          limit: 10
        })
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }

      const parsedResponse = await response.json();
      console.debug('Success response:', parsedResponse);
      
      // Store recommendations and open modal
      setRecommendations(parsedResponse);
      setIsModalOpen(true);
    } catch (error) {
      console.error('Error in onSubmitHandler:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    form,
    handleSubmit: form.handleSubmit(onSubmitHandler),
    isModalOpen,
    setIsModalOpen,
    recommendations,
    isLoading
  };
}

export default useLaunchpadForm;
