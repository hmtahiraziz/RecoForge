import type { PLRadioGroupRootProps, PLRadioGroupItemProps, PLRadioGroupLabelProps } from './PLRadioGroup.types';

import React, { forwardRef } from 'react';
import clsx from 'clsx';
import * as RadioGroupPrimitive from '@radix-ui/react-radio-group';
import * as LabelPrimitive from '@radix-ui/react-label';

import { PLRadioGroupStyles } from './PLRadioGroup.styles';

export const PLRadioGroupRoot = forwardRef<HTMLDivElement, PLRadioGroupRootProps>((props, ref) => {
  const {
    className,
    children,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    isInvalid,
    ...restProps
  } = props;

  const styles = PLRadioGroupStyles();

  return (
    <RadioGroupPrimitive.Root {...restProps} ref={ref} className={styles.root({ className })}>
      {children}
    </RadioGroupPrimitive.Root>
  );
});

PLRadioGroupRoot.displayName = 'PLRadioGroupRoot';

// -----------------------------------------------------------------------------

export const PLRadioGroupItem = forwardRef<HTMLButtonElement, PLRadioGroupItemProps>((props, forwardRef) => {
  const { className, classNames, ...restProps } = props;

  const styles = PLRadioGroupStyles();

  return (
    <RadioGroupPrimitive.Item
      {...restProps}
      className={styles.item({
        className: clsx(className, classNames?.root)
      })}
      ref={forwardRef}
    >
      <span className={styles.effect({ className: classNames?.effect })} aria-hidden="true" />

      <span className={styles.circle({ className: classNames?.circle })} style={{ pointerEvents: 'none' }}>
        <RadioGroupPrimitive.Indicator className={styles.indicator({ className: classNames?.indicator })} />
      </span>
    </RadioGroupPrimitive.Item>
  );
});

PLRadioGroupItem.displayName = 'PLRadioGroupItem';

// -----------------------------------------------------------------------------

export const PLRadioGroupItemLabel = forwardRef<HTMLLabelElement, PLRadioGroupLabelProps>((props, ref) => {
  const { className, children, ...restProps } = props;

  const styles = PLRadioGroupStyles();

  return (
    <LabelPrimitive.Root
      {...restProps}
      ref={ref}
      className={styles.label({
        className
      })}
    >
      {children}
    </LabelPrimitive.Root>
  );
});

PLRadioGroupItemLabel.displayName = 'PLRadioGroupItemLabel';
