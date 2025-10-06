import { tv } from 'tailwind-variants';

export const PLInputStyles = tv({
  slots: {
    root: `
    flex cursor-text items-center gap-1 rounded-md bg-surfacecolor-primary shadow-sm ring-1 ring-inset ring-bordercolor-primary 
    data-[disabled]:cursor-default data-[readonly]:cursor-default data-[disabled]:bg-surfacecolor-secondary
    data-[readonly]:bg-surfacecolor-secondary data-[disabled]:ring-bordercolor-primary data-[readonly]:ring-bordercolor-primary`,
    input: `readonly:text-textcolor-disabled size-full flex-1 appearance-none bg-transparent text-textcolor-primary outline-none 
      placeholder:text-textcolor-secondary/[.64] 
      disabled:text-textcolor-disabled`,
    leadingIcon: '',
    clearable: '',
    invalidIndicator: 'text-iconcolor-error',
    secureVisibilityToggle: '',
    trailingIcon: '',
  },
  variants: {
    isInvalid: {
      true: {
        root: 'ring-bordercolor-error',
      },
      false: {
        root: 'focus-within:ring-focuscolor-primary hover:ring-bordercolor-action focus-within:hover:ring-focuscolor-primary',
      },
    },
    size: {
      xs: {
        root: 'h-6 px-1.5',
        input: 'body-xs',
      },
      sm: {
        root: 'h-8 px-2',
        input: 'body-xs',
      },
      md: {
        root: 'h-10 px-3',
        input: 'body-sm',
      },
      lg: {
        root: 'h-10 px-3',
        input: 'body-md',
      },
    },
  },
  defaultVariants: {
    size: 'md',
    isInvalid: false,
  },
  compoundSlots: [
    {
      slots: [
        'leadingIcon',
        'clearable',
        'invalidIndicator',
        'secureVisibilityToggle',
        'trailingIcon',
      ],
      className: 'shrink-0',
    },
    {
      slots: ['leadingIcon', 'secureVisibilityToggle', 'trailingIcon'],
      className: 'text-iconcolor-secondary',
    },
    {
      slots: [
        'leadingIcon',
        'invalidIndicator',
        'secureVisibilityToggle',
        'trailingIcon',
      ],
      size: 'xs',
      className: 'size-3',
    },
    {
      slots: [
        'leadingIcon',
        'invalidIndicator',
        'secureVisibilityToggle',
        'trailingIcon',
      ],
      size: ['sm', 'md'],
      className: 'size-4',
    },
    {
      slots: [
        'leadingIcon',
        'invalidIndicator',
        'secureVisibilityToggle',
        'trailingIcon',
      ],
      size: 'lg',
      className: 'size-5',
    },
  ],
});
