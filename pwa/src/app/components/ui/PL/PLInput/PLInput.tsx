'use client';

import type { PLInputProps } from '@/app/components/ui/PL/PLInput/PLInput.types';

import React, { forwardRef, useRef } from 'react';

import { useComposedRefs } from '@radix-ui/react-compose-refs';
import { useControllableState } from '@radix-ui/react-use-controllable-state';

import clsx from 'clsx';

import { AppIcon } from '@/app/components/ui/Shared/AppIcon';
import { PLIconButton } from '@/app/components/ui/PL/PLIconButton';

import { cn } from '@/app/lib/utils/cn';
import { chainCallbacks } from '@/app/lib/utils/chainCallbacks';

import { PLInputStyles } from './PLInput.styles';

export const PLInput = forwardRef<HTMLInputElement, PLInputProps>((props, forwardRef) => {
  const {
    className,
    classNames,
    clearRef,
    type: pType = 'text',
    value: pValue,
    defaultValue: pDefaultValue,
    onValueChange,
    isSecureVisible: pIsSecureVisible,
    defaultIsSecureVisible: pDefaultIsSecureVisible = false,
    onIsSecureVisibleChange,
    disabled,
    readOnly,
    size = 'md',
    isInvalid,
    isClearable: pIsClearable,
    showInvalidIndicator,
    showToggleSecure,
    leadingIcon: pLeadingIcon,
    trailingIcon: pTrailingIcon,
    onClear,
    onChange,
    ...restProps
  } = props;

  const inputRef = useRef<HTMLInputElement | null>(null);
  const composedInputRefs = useComposedRefs(forwardRef, inputRef);

  const [value = '', setValue] = useControllableState({
    prop: pValue,
    defaultProp: pDefaultValue,
    onChange: onValueChange
  });

  const [isSecureVisible = false, setIsSecureVisible] = useControllableState({
    prop: pIsSecureVisible,
    defaultProp: pDefaultIsSecureVisible,
    onChange: onIsSecureVisibleChange
  });

  const isOriginalTypePassword = pType === 'password';
  const isDisabled = Boolean(disabled);
  const isReadOnly = Boolean(readOnly);
  const isClearable = Boolean(pIsClearable);
  const canShowClearable = Boolean(value) && isClearable && !isDisabled && !isReadOnly;
  const canShowInvalidIndicator = isInvalid && showInvalidIndicator;
  const canShowSecureVisibilityToggle = isOriginalTypePassword && showToggleSecure && !isDisabled && !isReadOnly;
  const inputType = isOriginalTypePassword && isSecureVisible ? 'text' : pType;

  const styles = PLInputStyles({ size, isInvalid });

  const leadingIcon = React.isValidElement(pLeadingIcon)
    ? React.cloneElement(pLeadingIcon, {
        // @ts-expect-error ignoring `'className' property does not exist` because it does.
        className: styles.leadingIcon({
          className: cn(classNames?.leadingIcon)
        }),
        'aria-hidden': true
      })
    : null;

  const trailingIcon = React.isValidElement(pTrailingIcon)
    ? React.cloneElement(pTrailingIcon, {
        // @ts-expect-error ignoring `'className' property does not exist` because it does.
        className: styles.trailingIcon({
          className: cn(classNames?.trailingIcon)
        }),
        'aria-hidden': true
      })
    : null;

  function handleOnClear() {
    setValue('');

    if (typeof onClear === 'function') {
      onClear();
    }

    inputRef.current?.focus();
  }

  return (
    <div
      className={styles.root({
        className: clsx(className, classNames?.root)
      })}
      data-readonly={isReadOnly ? '' : undefined}
      data-disabled={isDisabled ? '' : undefined}
      data-invalid={isInvalid ? '' : undefined}
      onClick={() => {
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }}
    >
      {leadingIcon}

      <input
        {...restProps}
        ref={composedInputRefs}
        className={styles.input({ className: classNames?.input })}
        type={inputType}
        disabled={isDisabled}
        readOnly={isReadOnly}
        value={value}
        onChange={
          isReadOnly && !onChange
            ? undefined
            : chainCallbacks(onChange, (event: React.ChangeEvent<HTMLInputElement>) => setValue(event.target.value))
        }
      />

      {canShowClearable && (
        <PLIconButton
          data-testid="pl-input-clear-button"
          ref={clearRef}
          className={styles.clearable({ className: classNames?.clearable })}
          hierarchy="primary"
          fill={false}
          size="sm"
          icon={<AppIcon name="delete-circle" />}
          onClick={handleOnClear}
        />
      )}

      {canShowInvalidIndicator && (
        <AppIcon
          className={styles.invalidIndicator({
            className: classNames?.invalidIndicator
          })}
          name="alert-information-circle"
        />
      )}

      {canShowSecureVisibilityToggle && (
        <button
          type="button"
          className={styles.secureVisibilityToggle({
            className: classNames?.secureVisibilityToggle
          })}
          onClick={(event) => {
            event.stopPropagation();
            setIsSecureVisible((prev) => !prev);
          }}
        >
          <AppIcon className="size-full" name={inputType === 'password' ? 'edit-view' : 'edit-view-off'} />
        </button>
      )}
      {trailingIcon}
    </div>
  );
});

PLInput.displayName = 'PLInput';
