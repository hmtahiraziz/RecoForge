import { tv } from 'tailwind-variants';

export const PLDropdownItemStyles = tv({
  slots: {
    root: 'flex w-full flex-1 items-start gap-2 rounded-sm bg-surfacecolor-primary px-4 py-2.5 outline-none hover:bg-surfacecolor-secondary focus:bg-surfacecolor-secondary',
    leadingIcon: 'size-6 shrink-0 text-iconcolor-secondary',
    mainWrapper: 'flex flex-1 flex-col items-start justify-start',
    labelCaptionWrapper: 'flex items-start justify-start gap-1',
    label: 'body-md text-left',
    caption: 'body-md text-left text-textcolor-disabled/50',
    description: 'body-sm text-left',
    selectedIcon: 'ml-auto size-5 shrink-0 self-center text-iconcolor-action',
  },
  variants: {
    selected: {
      true: '',
      false: '',
    },
    disabled: {
      true: {
        root: 'pointer-events-none cursor-not-allowed',
        label: 'text-textcolor-disabled',
        description: 'text-textcolor-disabled',
      },
      false: {
        root: 'cursor-pointer',
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
