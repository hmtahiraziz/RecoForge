/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-nocheck

'use client';

import type {
  PLSelectProviderProps,
  PLSelectRootProps,
  PLSelectTriggerProps,
  PLSelectContentProps,
  PLSelectDropdownItemProps,
  PLSelectMenuDefaultItemProps
} from './PLSelect.types';

import React, {
  cloneElement,
  createContext,
  forwardRef,
  isValidElement,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState
} from 'react';

import * as SelectPrimitive from '@radix-ui/react-select';
import { useControllableState } from '@radix-ui/react-use-controllable-state';
import { useComposedRefs } from '@radix-ui/react-compose-refs';
import { useSize } from '@radix-ui/react-use-size';

import clsx from 'clsx';

import { AppIcon } from '@/app/components/ui/Shared/AppIcon';
import { PLIconButton } from '@/app/components/ui/PL/PLIconButton';
import { PLDropdownItem } from '@/app/components/ui/PL/PLDropdownItem';
import { PLMenuDefaultItem } from '@/app/components/ui/PL/PLMenuDefaultItem';

import { PLSelectStyles } from './PLSelect.styles';

export const PLSelectGroup = SelectPrimitive.Group;

export const PLSelectValue = SelectPrimitive.Value;

export const PLSelectScrollUpButton = SelectPrimitive.ScrollUpButton;

export const PLSelectScrollDownButton = SelectPrimitive.ScrollDownButton;

export const PLSelectSeparator = SelectPrimitive.Separator;

export const PLSelectLabel = SelectPrimitive.Label;

export const PLSelectItem = SelectPrimitive.Item;

export const PLSelectItemText = SelectPrimitive.ItemText;

export const PLSelectItemIndicator = SelectPrimitive.ItemIndicator;

// -----------------------------------------------------------------------------

export const PLSelectContext = createContext<PLSelectProviderProps | null>(null);

// -----------------------------------------------------------------------------

export const PLSelectRoot = (props: PLSelectRootProps) => {
  const {
    value: pValue,
    defaultValue: pDefaultValue,
    onValueChange,
    open: pOpen,
    defaultOpen: pDefaultOpen,
    onOpenChange,
    disabled,
    isInvalid,
    isClearable,
    onClear,
    children,
    ...restProps
  } = props;

  const [options, setOptions] = useState<React.ReactElement[]>([]);

  const [value = '', setValue] = useControllableState({
    prop: pValue,
    // @ts-expect-error defaultProp is not required
    defaultProp: pDefaultValue,
    onChange: onValueChange
  });

  const [open, setOpen] = useControllableState({
    prop: pOpen,
    // @ts-expect-error defaultProp is not required
    defaultProp: pDefaultOpen,
    onChange: onOpenChange
  });

  return (
    <PLSelectContext.Provider
      value={{
        options,
        setOptions,
        value,
        setValue,
        open,
        setOpen,
        disabled,
        isInvalid,
        isClearable,
        onClear
      }}
    >
      <SelectPrimitive.Root
        {...restProps}
        open={open}
        onOpenChange={setOpen}
        value={value}
        onValueChange={setValue}
        disabled={disabled}
      >
        {children}
      </SelectPrimitive.Root>
    </PLSelectContext.Provider>
  );
};

PLSelectRoot.displayName = 'PLSelectRoot';

// -----------------------------------------------------------------------------

export const PLSelectTrigger = forwardRef<HTMLButtonElement, PLSelectTriggerProps>((props, ref) => {
  const {
    className,
    classNames,
    placeholder,
    size = 'md',
    disabled,
    isClearable: pIsClearable,
    isInvalid: pIsInvalid,
    showInvalidIndicator,
    showExpandIcon = true,
    leadingIcon: pLeadingIcon,
    trailingIcon: pTrailingIcon,
    ...restProps
  } = props;

  const context = useContext(PLSelectContext)!;

  const [selectedOption, setSelectedOption] = useState<React.ReactElement | null>(null);

  const [endContentNode, setEndContentNode] = useState<HTMLSpanElement | null>(null);
  const triggerCtaRef = useRef<HTMLButtonElement | null>(null);
  const composedTriggerRefs = useComposedRefs(ref, triggerCtaRef);

  const endContentNodeSize = useSize(endContentNode);

  const isDisabled = Boolean(context.disabled) || Boolean(disabled);
  const isInvalid = Boolean(context.isInvalid) || Boolean(pIsInvalid);
  const isClearable = Boolean(context?.isClearable) || Boolean(pIsClearable) || typeof context?.onClear === 'function';
  const canShowClearable = Boolean(context?.value) && isClearable && !isDisabled;
  const canShowInvalidIndicator = isInvalid && showInvalidIndicator;

  useEffect(() => {
    const match = context.options?.find((option: React.ReactElement) => option.props.value === context.value);

    if (match) {
      setSelectedOption(match);
    } else {
      setSelectedOption(null);
    }
  }, [context.value, context.options]);

  const styles = PLSelectStyles({
    open: context.open,
    size,
    isInvalid,
    canShowClearable
  });

  const leadingIcon = isValidElement(pLeadingIcon)
    ? cloneElement(pLeadingIcon, {
        className: styles.triggerLeadingIcon({
          className: classNames?.leadingIcon
        }),
        'aria-hidden': true,
        'data-testid': 'pl-select-trigger-leading-icon'
      })
    : null;

  const trailingIcon = isValidElement(pTrailingIcon)
    ? cloneElement(pTrailingIcon, {
        className: styles.triggerTrailingIcon({
          className: classNames?.trailingIcon
        }),
        'aria-hidden': true,
        'data-testid': 'pl-select-trigger-trailing-icon'
      })
    : null;

  function handleOnClear(event: React.MouseEvent<HTMLButtonElement>) {
    event.preventDefault();
    event.stopPropagation();

    context?.setValue?.('');
    context?.onClear?.();
  }

  const getClearableRightPosition = useCallback(() => {
    if (triggerCtaRef.current) {
      const GAP_BETWEEN_ITEMS = 4;

      const triggerCtaPaddingRight = parseInt(window.getComputedStyle(triggerCtaRef.current)?.paddingRight);
      const endContentWidth = endContentNodeSize?.width || 0;

      const total = triggerCtaPaddingRight + endContentWidth + GAP_BETWEEN_ITEMS;

      return total;
    }

    return 0;
  }, [endContentNodeSize]);

  return (
    <div
      className={styles.triggerRoot({
        className: clsx(className, classNames?.root)
      })}
      data-disabled={isDisabled ? '' : undefined}
    >
      <SelectPrimitive.Trigger
        data-testid="pl-select-trigger"
        {...restProps}
        ref={composedTriggerRefs}
        className={styles.triggerCta({ className: classNames?.cta })}
        disabled={isDisabled}
      >
        {leadingIcon}

        <SelectPrimitive.Value placeholder={placeholder} data-slot="value">
          {selectedOption?.props.children ?? ''}
        </SelectPrimitive.Value>

        <span
          ref={(node) => setEndContentNode(node)}
          className={styles.triggerEndContent({
            className: classNames?.endContent
          })}
        >
          {canShowInvalidIndicator && (
            <AppIcon
              className={styles.triggerInvalidIndicator({
                className: classNames?.invalidIndicator
              })}
              name="alert-information-circle"
              aria-hidden="true"
              data-testid="pl-select-trigger-invalid-indicator"
            />
          )}

          {trailingIcon}

          {showExpandIcon && (
            <SelectPrimitive.Icon asChild>
              <AppIcon
                className={styles.triggerExpandIcon({
                  className: classNames?.expandIcon
                })}
                name="arrows-chevron-down-mini"
                data-testid="pl-select-trigger-expand-icon"
              />
            </SelectPrimitive.Icon>
          )}
        </span>
      </SelectPrimitive.Trigger>

      {canShowClearable && (
        <PLIconButton
          className={styles.triggerClearable({
            className: classNames?.clearable
          })}
          style={{
            right: getClearableRightPosition()
          }}
          hierarchy="primary"
          fill={false}
          size="sm"
          icon={<AppIcon name="delete-circle" aria-hidden="true" />}
          onClick={handleOnClear}
          aria-label="Clear value"
          data-testid="pl-select-trigger-clearable"
        />
      )}
    </div>
  );
});

PLSelectTrigger.displayName = 'PLSelectTrigger';

// -----------------------------------------------------------------------------

export const PLSelectContent = forwardRef<HTMLDivElement, PLSelectContentProps>((props, ref) => {
  const {
    className,
    classNames,
    viewportRef,
    children,
    beforeViewportContent,
    afterViewportContent,
    position = 'popper',
    side = 'bottom',
    sideOffset = 8,
    align = 'start',
    alignOffset = 0,
    ...restProps
  } = props;

  const { setOptions } = useContext(PLSelectContext);

  const options = useMemo(() => React.Children.toArray(children).filter(React.isValidElement), [children]);

  useEffect(() => {
    if (typeof setOptions !== 'function') return;

    if (Array.isArray(options)) {
      setOptions(options);
    } else {
      setOptions([]);
    }
  }, [options, setOptions]);

  const hasBeforeViewportContent = Boolean(beforeViewportContent);
  const hasAfterViewportContent = Boolean(afterViewportContent);

  const styles = PLSelectStyles();

  return (
    <SelectPrimitive.Portal>
      <SelectPrimitive.Content
        data-testid="pl-select-content"
        {...restProps}
        ref={ref}
        className={styles.content({
          className: clsx(className, classNames?.root)
        })}
        position={position}
        side={side}
        sideOffset={sideOffset}
        align={align}
        alignOffset={alignOffset}
      >
        {hasBeforeViewportContent ? beforeViewportContent : null}

        <SelectPrimitive.Viewport
          ref={viewportRef}
          className={styles.viewport({ className: classNames?.viewport })}
          data-testid="pl-select-viewport"
        >
          {children}
        </SelectPrimitive.Viewport>

        {hasAfterViewportContent ? afterViewportContent : null}
      </SelectPrimitive.Content>
    </SelectPrimitive.Portal>
  );
});

PLSelectContent.displayName = 'PLSelectContent';

// -----------------------------------------------------------------------------

export const PLSelectDropdownItem = forwardRef<HTMLDivElement, PLSelectDropdownItemProps>((props, ref) => {
  const { className, value, children, disabled, ...restProps } = props;

  const context = useContext(PLSelectContext);

  const isSelected = context?.value === value;

  return (
    <SelectPrimitive.Item {...restProps} ref={ref} className={className} value={value} asChild>
      <PLDropdownItem disabled={disabled} selected={isSelected} asChild>
        <div>
          <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
        </div>
      </PLDropdownItem>
    </SelectPrimitive.Item>
  );
});

PLSelectDropdownItem.displayName = 'PLSelectDropdownItem';

// -----------------------------------------------------------------------------

export const PLSelectMenuDefaultItem = forwardRef<HTMLDivElement, PLSelectMenuDefaultItemProps>((props, ref) => {
  const { className, value, children, ...restProps } = props;

  const context = useContext(PLSelectContext);

  const isSelected = context?.value === value;

  return (
    <SelectPrimitive.Item {...restProps} ref={ref} className={className} value={value} asChild>
      <PLMenuDefaultItem selected={isSelected} asChild>
        <div>
          <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
        </div>
      </PLMenuDefaultItem>
    </SelectPrimitive.Item>
  );
});

PLSelectMenuDefaultItem.displayName = 'PLSelectMenuDefaultItem';
