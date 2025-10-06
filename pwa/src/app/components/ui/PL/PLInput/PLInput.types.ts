import React from 'react';

export interface PLInputGenericProps<T> extends Omit<React.ComponentPropsWithRef<'input'>, 'size'> {
  clearRef?: React.LegacyRef<HTMLButtonElement>;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  isInvalid?: boolean;
  isClearable?: boolean;
  showInvalidIndicator?: boolean;
  showToggleSecure?: boolean;
  isSecureVisible?: boolean;
  defaultIsSecureVisible?: boolean;
  leadingIcon?: React.ReactElement;
  trailingIcon?: React.ReactElement;
  onValueChange?: (value: T) => void;
  onClear?: () => void;
  onIsSecureVisibleChange?: (isSecureVisible: boolean) => void;
  classNames?: {
    root?: string;
    leadingIcon?: string;
    trailingIcon?: string;
    input?: string;
    clearable?: string;
    invalidIndicator?: string;
    secureVisibilityToggle?: string;
  };
}

export type PLInputProps = PLInputGenericProps<React.ComponentPropsWithRef<'input'>['value']>;
