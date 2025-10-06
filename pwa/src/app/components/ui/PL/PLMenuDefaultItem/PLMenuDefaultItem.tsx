import type { PLMenuDefaultItemProps } from './PLMenuDefaultItem.types';

import React, { forwardRef } from 'react';

import { Slot } from '@radix-ui/react-slot';

import clsx from 'clsx';

import { AppIcon } from '@/app/components/ui/Shared/AppIcon';

import { getSubtree } from '@/app/lib/utils/getSubtree';

import { PLMenuDefaultItemStyles } from './PLMenuDefaultItem.styles';

export const PLMenuDefaultItem = forwardRef<HTMLButtonElement, PLMenuDefaultItemProps>((props, ref) => {
  const { className, classNames, asChild, leadingIcon, description, selected, disabled, children, ...restProps } =
    props;

  const hasDescription = Boolean(description);

  const styles = PLMenuDefaultItemStyles({ disabled, selected });

  const Comp = asChild ? Slot : 'button';

  return (
    <Comp
      {...restProps}
      ref={ref}
      className={styles.root({
        className: clsx(className, classNames?.root)
      })}
      type="button"
      disabled={disabled}
      data-disabled={disabled ? '' : undefined}
      data-testid="pl-menu-default-item"
    >
      {/* @ts-expect-error getSubtree returns ReactNode but we need to pass ReactElement */}
      {getSubtree({ asChild, children }, (content) => {
        return (
          <React.Fragment>
            {React.isValidElement(leadingIcon)
              ? React.cloneElement(leadingIcon, {
                  // @ts-expect-error ignoring `'className' property does not exist` because it does.
                  className: styles.leadingIcon({
                    className: classNames?.leadingIcon
                  }),
                  'data-testid': 'pl-menu-default-item-leading-icon'
                })
              : null}

            <div
              className={styles.contentWrapper({
                className: classNames?.contentWrapper
              })}
            >
              <div
                className={styles.label({
                  className: classNames?.label
                })}
                data-testid="pl-menu-default-item-label"
              >
                {content}
              </div>

              {hasDescription ? (
                <p
                  className={styles.description({
                    className: classNames?.description
                  })}
                  data-testid="pl-menu-default-item-description"
                >
                  {description}
                </p>
              ) : null}
            </div>

            {selected && (
              <AppIcon
                className={styles.selectedIcon({
                  className: classNames?.selectedIcon
                })}
                name="validation-check"
                data-testid="pl-menu-default-item-selected-icon"
              />
            )}
          </React.Fragment>
        );
      })}
    </Comp>
  );
});

PLMenuDefaultItem.displayName = 'PLMenuDefaultItem';
