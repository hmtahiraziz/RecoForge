import type { PLButtonProps } from './PLButton.types';

import React, { forwardRef } from 'react';
import { Slot } from '@radix-ui/react-slot';
import { AppIcon } from '@/app/components/ui/Shared/AppIcon';
import { getSubtree } from '@/app/lib/utils/getSubtree';
import { PLButtonStyles } from './PLButton.styles';

export const PLButton = forwardRef<HTMLButtonElement, PLButtonProps>((props, forwardRef) => {
  const {
    className,
    asChild,
    hierarchy = 'secondary',
    size = 'md',
    type = 'button',
    disabled = props.isLoading,
    isLoading = false,
    icon,
    leadingIcon,
    trailingIcon,
    children,
    ...restProps
  } = props;

  const isDisabled = Boolean(disabled) || Boolean(isLoading);
  const isIconOnly = Boolean(icon);
  const hasValidIcon = React.isValidElement(icon);
  const hasValidLeadingIcon = React.isValidElement(leadingIcon);
  const hasValidTrailingIcon = React.isValidElement(trailingIcon);

  const styles = PLButtonStyles({
    hierarchy,
    size,
    isIconOnly
  });

  const clonedIcon = hasValidIcon
    ? React.cloneElement(icon, {
        className: styles.icon({ className: icon?.props.className })
      })
    : undefined;

  const clonedLeadingIcon = hasValidLeadingIcon
    ? React.cloneElement(leadingIcon, {
        className: styles.icon({ className: leadingIcon?.props.className })
      })
    : undefined;

  const clonedTrailingIcon = hasValidTrailingIcon
    ? React.cloneElement(trailingIcon, {
        className: styles.icon({ className: trailingIcon?.props.className })
      })
    : undefined;

  const Comp = asChild ? Slot : 'button';

  return (
    <Comp
      {...restProps}
      ref={forwardRef}
      className={styles.root({ className })}
      type={type}
      disabled={isDisabled}
      data-disabled={isDisabled ? '' : undefined}
      data-loading={isLoading ? '' : undefined}
      aria-disabled={isDisabled}
    >
      {/* @ts-expect-error getSubtree returns ReactNode but we need to pass ReactElement */}
      {getSubtree({ asChild, children }, (child) => {
        const innerContent = (
          <React.Fragment>
            {!isIconOnly && clonedLeadingIcon}
            {isIconOnly && clonedIcon}
            {child}
            {!isIconOnly && clonedTrailingIcon}
          </React.Fragment>
        );

        if (!isLoading) {
          return innerContent;
        }

        return (
          <React.Fragment>
            <span className="invisible contents" aria-hidden="true">
              {innerContent}
            </span>

            <span className="sr-only" data-testid="button-loading-accessible-content">
              {innerContent}
            </span>

            <div className="absolute inset-0 m-auto flex items-center justify-center" data-testid="button-spinner">
              <AppIcon
                className={styles.icon({ className: 'animate-spin' })}
                name="spinner"
                aria-hidden="true"
                focusable="false"
              />
            </div>
          </React.Fragment>
        );
      })}
    </Comp>
  );
});

PLButton.displayName = 'PLButton';
