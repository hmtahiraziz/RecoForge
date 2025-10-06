'use client';

import React, { forwardRef } from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cn } from '@/app/lib/utils/cn';
import { getSubtree } from '@/app/lib/utils/getSubtree';
import { PWStepsItemStyles } from './PWSteps.styles';

import ValidationCheckIcon from '@/app/icons/validation-check.svg';

import type { PWStepsContextProps, PWStepsRootProps, PWStepsItemProps } from './PWSteps.types';

// -----------------------------------------------------------------------------

export const PWStepsContext = React.createContext<PWStepsContextProps | null>(null);

// -----------------------------------------------------------------------------

export const PWStepsRoot = forwardRef<HTMLDivElement, PWStepsRootProps>((props, forwardRef) => {
  const { className, step, asChild, children, ...restProps } = props;

  const Comp = asChild ? Slot : 'div';

  return (
    <PWStepsContext.Provider value={{ step }}>
      <Comp {...restProps} ref={forwardRef} className={cn('group/steps flex items-center', className)} data-step={step}>
        {children}
      </Comp>
    </PWStepsContext.Provider>
  );
});

PWStepsRoot.displayName = 'PWStepsRoot';

// -----------------------------------------------------------------------------

export const PWStepsItem = forwardRef<HTMLDivElement, PWStepsItemProps>((props, forwardRef) => {
  const { className, index, asChild, children, ...restProps } = props;

  const Comp = asChild ? Slot : 'div';

  const ctx = React.useContext(PWStepsContext);

  if (!ctx) {
    console.warn('PWSteps.Item must be used within a PWSteps.Root component');
    return;
  }

  const isActive = ctx.step === index;
  const isCompleted = ctx.step > index;
  const state = isCompleted ? 'completed' : isActive ? 'active' : 'inactive';

  const styles = PWStepsItemStyles({ state });

  return (
    <Comp {...restProps} ref={forwardRef} className={styles.root({ className })} data-state={state} data-index={index}>
      {/* @ts-expect-error getSubtree returns ReactNode but we need to pass ReactElement */}
      {getSubtree({ asChild, children }, (child: React.ReactNode) => {
        return (
          <React.Fragment>
            <div className={styles.indicator()}>
              {isCompleted ? <ValidationCheckIcon className={styles.icon()} /> : child}
            </div>

            <div className={styles.separator()} aria-hidden="true" />
          </React.Fragment>
        );
      })}
    </Comp>
  );
});

PWStepsItem.displayName = 'PWStepsItem';
