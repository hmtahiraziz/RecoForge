'use client';

import type {
  PLFormFieldContextProps,
  PLFormFieldRootProps,
  PLFormFieldControlProps,
  PLFormFieldLabelProps,
  PLFormFieldDescriptionProps,
  PLFormFieldErrorProps
} from './PLFormField.types';

import React, { createContext, forwardRef, useContext, useMemo, useState } from 'react';

import { Slot } from '@radix-ui/react-slot';
import * as LabelPrimitive from '@radix-ui/react-label';
import { useComposedRefs } from '@radix-ui/react-compose-refs';

import { useSafeId } from '@/app/hooks/useSafeId';
import { cn } from '@/app/lib/utils/cn';

const PLFormFieldContext = createContext<PLFormFieldContextProps>({});

function usePLFormFieldContext() {
  const context = useContext(PLFormFieldContext);

  if (Object.keys(context).length === 0) {
    throw new Error('usePLFormFieldContext must be used within a PLFormFieldContext');
  }

  return context;
}

export const PLFormFieldRoot = forwardRef<HTMLDivElement, PLFormFieldRootProps>((props, ref) => {
  const { className, asChild, children, isInvalid = false, showBothFeedback = false, ...restProps } = props;

  const [descriptionNode, setDescriptionNode] = useState<HTMLParagraphElement | null>(null);
  const [errorNode, setErrorNode] = useState<HTMLParagraphElement | null>(null);

  const id = useSafeId(props.id);
  const itemId = `${id}-item`;
  const descriptionId = `${id}-description`;
  const errorId = `${id}-error`;

  const hasDescriptionElement = Boolean(descriptionNode);
  const hasErrorElement = Boolean(errorNode);

  const Comp = asChild ? Slot : 'div';

  return (
    <PLFormFieldContext.Provider
      value={{
        setDescriptionNode,
        setErrorNode,
        id,
        itemId,
        descriptionId,
        errorId,
        hasDescriptionElement,
        hasErrorElement,
        isInvalid,
        showBothFeedback
      }}
    >
      <Comp {...restProps} ref={ref} className={cn('flex flex-col gap-1.5', className)}>
        {children}
      </Comp>
    </PLFormFieldContext.Provider>
  );
});

PLFormFieldRoot.displayName = 'PLFormFieldRoot';

// -----------------------------------------------------------------------------

export const PLFormFieldControl = forwardRef<HTMLElement, PLFormFieldControlProps>((props, ref) => {
  const { children } = props;

  const { itemId, descriptionId, errorId, hasDescriptionElement, hasErrorElement, showBothFeedback, isInvalid } =
    usePLFormFieldContext();

  const describedBy = useMemo(() => {
    if (!hasDescriptionElement && !hasErrorElement) {
      return undefined;
    }

    if (showBothFeedback) {
      return [hasDescriptionElement ? descriptionId : undefined, isInvalid && hasErrorElement ? errorId : undefined]
        .filter(Boolean)
        .join(' ');
    }

    if (isInvalid && hasErrorElement) {
      return errorId;
    }

    return descriptionId;
  }, [descriptionId, errorId, hasDescriptionElement, hasErrorElement, isInvalid, showBothFeedback]);

  return (
    <Slot
      ref={ref}
      id={itemId}
      data-invalid={isInvalid ? '' : undefined}
      aria-invalid={isInvalid}
      aria-describedby={describedBy}
      // @ts-expect-error ignoring `'isInvalid' property does not exist` because it does.
      isInvalid={isInvalid}
    >
      {children}
    </Slot>
  );
});

PLFormFieldControl.displayName = 'PLFormFieldControl';

// -----------------------------------------------------------------------------

export const PLFormFieldLabel = forwardRef<HTMLLabelElement, PLFormFieldLabelProps>((props, ref) => {
  const { className, asChild, children, ...restProps } = props;

  const { itemId } = usePLFormFieldContext();

  const Comp = asChild ? Slot : LabelPrimitive.Root;

  if (!children) {
    return null;
  }

  return (
    <Comp {...restProps} ref={ref} className={cn('text-heading-sm text-textcolor-secondary', className)} htmlFor={itemId}>
      {children}
    </Comp>
  );
});

PLFormFieldLabel.displayName = 'PLFormFieldLabel';

// -----------------------------------------------------------------------------

export const PLFormFieldDescription = forwardRef<HTMLParagraphElement, PLFormFieldDescriptionProps>((props, ref) => {
  const { className, asChild, children, ...restProps } = props;

  const { descriptionId, setDescriptionNode, isInvalid, showBothFeedback, hasErrorElement } = usePLFormFieldContext();

  const composedRefs = useComposedRefs(ref, (node) => setDescriptionNode?.(node));

  const Comp = asChild ? Slot : 'p';

  if (!showBothFeedback && isInvalid && hasErrorElement) {
    return null;
  }

  if (!children) {
    return null;
  }

  return (
    <Comp
      {...restProps}
      ref={composedRefs}
      id={descriptionId}
      className={cn('text-body-xs text-textcolor-secondary', className)}
    >
      {children}
    </Comp>
  );
});

PLFormFieldDescription.displayName = 'PLFormFieldDescription';

// -----------------------------------------------------------------------------

export const PLFormFieldError = forwardRef<HTMLParagraphElement, PLFormFieldErrorProps>((props, ref) => {
  const { className, asChild, children, ...restProps } = props;

  const { errorId, setErrorNode, isInvalid } = usePLFormFieldContext();

  const composedRefs = useComposedRefs(ref, (node) => setErrorNode?.(node));

  const Comp = asChild ? Slot : 'p';

  if (!isInvalid) {
    return null;
  }

  if (!children) {
    return null;
  }

  return (
    <Comp {...restProps} ref={composedRefs} id={errorId} className={cn('text-body-xs text-textcolor-error', className)}>
      {children}
    </Comp>
  );
});

PLFormFieldError.displayName = 'PLFormFieldError';
