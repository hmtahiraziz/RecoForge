import React from 'react';
import { LabelProps } from '@radix-ui/react-label';

export interface PLFormFieldContextProps {
  setDescriptionNode?: React.Dispatch<React.SetStateAction<HTMLParagraphElement | null>>;
  setErrorNode?: React.Dispatch<React.SetStateAction<HTMLParagraphElement | null>>;
  id?: string;
  itemId?: string;
  descriptionId?: string;
  errorId?: string;
  hasDescriptionElement?: boolean;
  hasErrorElement?: boolean;
  isInvalid?: boolean;
  showBothFeedback?: boolean;
}

export interface PLFormFieldRootProps extends React.ComponentPropsWithRef<'div'> {
  asChild?: boolean;
  isInvalid?: boolean;
  showBothFeedback?: boolean;
}

export interface PLFormFieldControlProps {
  children: React.ReactNode;
}

export type PLFormFieldLabelProps = LabelProps;

export interface PLFormFieldDescriptionProps extends React.ComponentPropsWithRef<'p'> {
  asChild?: boolean;
}

export interface PLFormFieldErrorProps extends React.ComponentPropsWithRef<'p'> {
  asChild?: boolean;
}