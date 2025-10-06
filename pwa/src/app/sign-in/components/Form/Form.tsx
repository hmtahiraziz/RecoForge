'use client';

import React from 'react';

import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';

import { PLFormField } from '@/app/components/ui/PL/PLFormField';
import { PLInput } from '@/app/components/ui/PL/PLInput';
import { PLButton } from '@/app/components/ui/PL/PLButton/PLButton';
import { Controller, useForm } from 'react-hook-form';
import { GET_LOGIN_DETAILS } from '@/app/lib/graphql/user.gql';
import { apolloClient } from '@/app/lib/graphql/apolloClient';
import { useUserContext } from '@/app/providers/UserContextProvider';
import { storeCookie } from '@/app/actions/cookies/cookies';
import { useRouter } from 'next/navigation';

interface UserDataResponse {
  loginAdminUser: {
    accessToken: string;
    adminUser: {
      email: string;
      id: string;
      role: string;
    };
  };
}

const schema = yup.object().shape({
  email: yup.string().email('Invalid email address.').required('Please enter your email.'),
  password: yup.string().required('Please enter your password.')
});

export const Form = () => {
  const { handleSubmit, control, formState } = useForm({
    resolver: yupResolver(schema)
  });

  const { setUser } = useUserContext();

  const router = useRouter();

  const onSubmit = async (data: any) => {
    const response = await apolloClient.mutate<UserDataResponse>({
      mutation: GET_LOGIN_DETAILS,
      variables: {
        email: data.email,
        password: data.password
      }
    });

    const userData = response.data?.loginAdminUser;

    if (!userData) {
      throw new Error('Failed to login');
    }

    const userDataToStore = {
      token: userData?.accessToken,
      ...userData?.adminUser
    };

    await storeCookie('user', userDataToStore);

    setUser(userDataToStore);

    router.push('/');
  };

  return (
    <form className="flex flex-col gap-6" onSubmit={handleSubmit(onSubmit)}>
      <Controller
        control={control}
        name="email"
        render={({ field, fieldState }) => (
          <PLFormField.Root isInvalid={fieldState.invalid} showBothFeedback>
            <PLFormField.Label>Email</PLFormField.Label>
            <PLFormField.Control>
              <PLInput {...field} placeholder="E.g. olivia@botti.com" showInvalidIndicator />
            </PLFormField.Control>
            <PLFormField.Error> {fieldState.error?.message}</PLFormField.Error>
          </PLFormField.Root>
        )}
      />

      <Controller
        control={control}
        name="password"
        render={({ field, fieldState }) => (
          <PLFormField.Root isInvalid={fieldState.invalid} showBothFeedback>
            <PLFormField.Label>Password</PLFormField.Label>
            <PLFormField.Control>
              <PLInput
                {...field}
                placeholder="****************"
                type="password"
                showToggleSecure={!fieldState.invalid}
                showInvalidIndicator
              />
            </PLFormField.Control>
            <PLFormField.Error>{fieldState.error?.message}</PLFormField.Error>
          </PLFormField.Root>
        )}
      />

      <PLButton isLoading={formState.isSubmitting} hierarchy="primary" type="submit">
        Sign In
      </PLButton>
    </form>
  );
};
