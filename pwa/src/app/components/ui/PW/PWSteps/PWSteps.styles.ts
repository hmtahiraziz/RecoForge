import { tv, type VariantProps } from 'tailwind-variants';

export const PWStepsItemStyles = tv({
  slots: {
    root: 'group/steps-item inline-flex shrink-0 items-center',
    indicator:
      'group/steps-indicator text-body-xs inline-flex size-6 shrink-0 items-center justify-center rounded-full text-center',
    icon: 'size-4',
    separator: 'h-0.5 w-4 shrink-0 group-last-of-type/steps-item:hidden',
  },
  variants: {
    state: {
      inactive: {
        indicator: 'bg-surfacecolor-tertiary text-textcolor-primary',
        separator: 'bg-surfacecolor-tertiary',
      },
      active: {},
      completed: {},
    },
  },
  compoundVariants: [
    {
      state: ['active', 'completed'],
      className: {
        indicator: 'bg-surfacecolor-action text-textcolor-tertiary',
        separator: 'bg-surfacecolor-action',
      },
    },
  ],
  defaultVariants: {
    state: 'inactive',
  },
});

export type PWStepsItemStylesVariants = VariantProps<typeof PWStepsItemStyles>;
