import { PLDropdownItemProps } from './PLDropdownItem.types';

import React, { forwardRef } from 'react';

import { Slot } from '@radix-ui/react-slot';

import { getSubtree } from '@/app/lib/utils/getSubtree';

import { AppIcon } from '@/app/components/ui/Shared/AppIcon';

import clsx from 'clsx';

import { PLDropdownItemStyles } from './PLDropdownItem.styles';

export const PLDropdownItem = forwardRef<HTMLButtonElement, PLDropdownItemProps>((props, ref) => {
  const {
    className,
    classNames,
    asChild,
    leadingIcon,
    description,
    caption,
    selected,
    disabled,
    children,
    ...restProps
  } = props;

  const hasDescription = Boolean(description);
  const hasCaption = Boolean(caption);
  const hasValidLeadingIcon = React.isValidElement(leadingIcon);

  const styles = PLDropdownItemStyles({ selected, disabled });

  const clonedLeadingIcon = hasValidLeadingIcon
    ? React.cloneElement(leadingIcon, {
        // @ts-expect-error ignoring `'className' property does not exist` because it does.
        className: styles.leadingIcon(),
        'data-testid': 'pl-dropdown-item-leading-icon'
      })
    : undefined;

  const Comp = asChild ? Slot : 'button';

  return (
    <Comp
      data-testid="pl-dropdown-item"
      {...restProps}
      ref={ref}
      className={styles.root({
        className: clsx(className, classNames?.root)
      })}
      disabled={disabled}
      data-disabled={disabled ? '' : undefined}
    >
      {/* @ts-expect-error getSubtree returns ReactNode but we need to pass ReactElement */}

      {getSubtree({ asChild, children }, (content) => (
        <React.Fragment>
          {clonedLeadingIcon}

          <div
            className={styles.mainWrapper({
              className: classNames?.mainWrapper
            })}
          >
            <div
              className={styles.labelCaptionWrapper({
                className: classNames?.labelCaptionWrapper
              })}
            >
              <div
                className={styles.label({
                  className: classNames?.label
                })}
                data-testid="pl-dropdown-item-label"
              >
                {content}
              </div>

              {hasCaption && (
                <span
                  className={styles.caption({
                    className: classNames?.caption
                  })}
                  data-testid="pl-dropdown-item-caption"
                >
                  {caption}
                </span>
              )}
            </div>

            {hasDescription && (
              <p
                className={styles.description({
                  className: classNames?.description
                })}
                data-testid="pl-dropdown-item-description"
              >
                {description}
              </p>
            )}
          </div>

          {selected && (
            <AppIcon
              className={styles.selectedIcon({
                className: classNames?.selectedIcon
              })}
              name="validation-check"
              data-testid="pl-dropdown-item-selected-icon"
            />
          )}
        </React.Fragment>
      ))}
    </Comp>
  );
});

PLDropdownItem.displayName = 'PLDropdownItem';
