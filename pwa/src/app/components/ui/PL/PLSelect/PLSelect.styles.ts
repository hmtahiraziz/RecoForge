import { tv } from 'tailwind-variants';

export const PLSelectStyles = tv({
  slots: {
    triggerRoot: 'relative flex items-center',
    triggerCta:
      'group/select-trigger-cta flex w-full flex-1 cursor-pointer items-center gap-1 rounded-md bg-surfacecolor-primary shadow-sm outline-none ring-1 ring-inset ring-bordercolor-primary disabled:cursor-default disabled:bg-surfacecolor-secondary disabled:ring-bordercolor-primary [&>span[data-slot="value"]]:line-clamp-1 [&>span[data-slot="value"]]:w-full [&>span[data-slot="value"]]:flex-1 [&>span[data-slot="value"]]:text-left [&>span[data-slot="value"]]:text-textcolor-primary [&>span[data-slot="value"]]:data-[placeholder]:text-textcolor-secondary/[.64]',
    triggerLeadingIcon: 'text-iconcolor-secondary',
    triggerInvalidIndicator: 'text-iconcolor-error',
    triggerTrailingIcon: 'text-iconcolor-secondary',
    triggerExpandIcon:
      'text-iconcolor-action group-disabled/select-trigger-cta:text-iconcolor-secondary',
    triggerClearable: 'absolute z-50',
    triggerEndContent: 'flex items-center gap-1',
    content:
      'relative z-50 max-h-[var(--radix-select-content-available-height)] max-w-[var(--radix-select-content-available-width)] overflow-hidden rounded-md border border-solid border-bordercolor-primary bg-surfacecolor-primary py-1 shadow-lg',
    viewport: 'w-full min-w-[var(--radix-select-trigger-width)]',
  },
  variants: {
    open: {
      true: {
        triggerExpandIcon: '-rotate-180',
      },
    },
    isInvalid: {
      true: {
        triggerCta: 'ring-bordercolor-error',
      },
      false: {
        triggerCta:
          'focus-within:ring-focuscolor-primary hover:ring-bordercolor-action focus-within:hover:ring-focuscolor-primary',
      },
    },
    size: {
      xs: {
        triggerCta: '[&>span[data-slot="value"]]:body-xs h-6 px-1.5',
      },
      sm: {
        triggerCta: '[&>span[data-slot="value"]]:body-xs h-8 px-2',
      },
      md: {
        triggerCta: '[&>span[data-slot="value"]]:body-sm h-10 px-3',
      },
      lg: {
        triggerCta: '[&>span[data-slot="value"]]:body-md h-10 px-3',
      },
    },
    canShowClearable: {
      true: {
        triggerCta: '[&>span[data-slot="value"]]:mr-[1.75rem]',
      },
    },
  },
  compoundSlots: [
    {
      slots: [
        'triggerLeadingIcon',
        'triggerInvalidIndicator',
        'triggerTrailingIcon',
        'triggerExpandIcon',
      ],
      size: 'xs',
      className: 'size-3',
    },
    {
      slots: [
        'triggerLeadingIcon',
        'triggerInvalidIndicator',
        'triggerTrailingIcon',
        'triggerExpandIcon',
      ],
      size: ['sm', 'md'],
      className: 'size-4',
    },
    {
      slots: [
        'triggerLeadingIcon',
        'triggerInvalidIndicator',
        'triggerTrailingIcon',
        'triggerExpandIcon',
      ],
      size: 'lg',
      className: 'size-5',
    },
  ],
  defaultVariants: {
    open: false,
    size: 'md',
    isInvalid: false,
    canShowClearable: false,
  },
});
