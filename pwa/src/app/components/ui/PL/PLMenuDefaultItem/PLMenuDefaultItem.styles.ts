import { tv } from 'tailwind-variants';

export const PLMenuDefaultItemStyles = tv({
  slots: {
    root: 'flex w-full flex-1 items-center gap-2 rounded-sm bg-surfacecolor-primary px-6 py-3 outline-none hover:bg-surfacecolor-secondary focus:bg-surfacecolor-secondary',
    leadingIcon: 'size-4 shrink-0',
    contentWrapper: 'flex flex-1 flex-col items-start',
    label: 'body-sm text-left',
    description: 'body-xs text-left',
    selectedIcon: 'ml-auto size-3 shrink-0 self-center text-iconcolor-primary',
  },
  variants: {
    selected: {
      true: '',
      false: '',
    },
    disabled: {
      true: {
        root: 'cursor-not-allowed',
        leadingIcon: 'text-iconcolor-secondary',
        label: 'text-textcolor-disabled',
        description: 'text-textcolor-disabled',
      },
      false: {
        root: 'cursor-pointer',
        leadingIcon: 'text-iconcolor-action',
        label: 'text-textcolor-primary',
        description: 'text-textcolor-secondary',
      },
    },
  },
  compoundVariants: [
    {
      disabled: false,
      selected: true,
      className: {
        root: 'bg-surfacecolor-secondary',
      },
    },
  ],
});
