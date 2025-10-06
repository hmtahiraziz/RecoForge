'use client';

import type { PLIconButtonProps } from './PLIconButton.types';
import React, { forwardRef } from 'react';
import { Slot } from '@radix-ui/react-slot';
import { getSubtree } from '@/app/lib/utils/getSubtree';
import { PLIconButtonStyles } from './PLIconButton.styles';

export const PLIconButton = forwardRef<HTMLButtonElement, PLIconButtonProps>((props, forwardRef) => {
  const {
    className,
    type = 'button',
    disabled = false,
    icon,
    asChild,
    hierarchy = 'primary',
    size = 'md',
    fill = false,
    children,
    ...restProps
  } = props;

  const styles = PLIconButtonStyles({ hierarchy, size, fill });

  const hasValidIcon = React.isValidElement(icon);

  const clonedIcon = hasValidIcon
    ? React.cloneElement(icon, {
        className: styles.icon({ className: icon?.props.className })
      })
    : undefined;

  const Comp = asChild ? Slot : 'button';

  return (
    <Comp
      {...restProps}
      ref={forwardRef}
      className={styles.root({ className })}
      type={type}
      disabled={disabled}
      data-disabled={disabled ? '' : undefined}
      aria-disabled={disabled}
    >
      {/* @ts-expect-error getSubtree returns ReactNode but we need to pass ReactElement */}
      {getSubtree({ asChild, children }, (child) => (
        <React.Fragment>
          {clonedIcon}
          {child}
        </React.Fragment>
      ))}
    </Comp>
  );
});

PLIconButton.displayName = 'PLIconButton';
