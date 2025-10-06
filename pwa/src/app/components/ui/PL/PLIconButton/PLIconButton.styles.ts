import { tv } from 'tailwind-variants';

export const PLIconButtonStyles = tv({
  slots: {
    root: 'group/button relative inline-flex items-center justify-center rounded-full text-center outline-none ring-inset transition duration-[100ms] ease-brand focus:ring-2 focus:ring-focuscolor-primary aria-disabled:pointer-events-none aria-disabled:cursor-not-allowed',
    icon: ''
  },
  variants: {
    hierarchy: {
      primary: {
        root: ''
      },
      secondary: {
        root: ''
      },
      destructive: {
        root: ''
      }
    },
    size: {
      xs: {
        root: 'size-5',
        icon: 'size-3'
      },
      sm: {
        root: 'size-6',
        icon: 'size-4'
      },
      md: {
        root: 'size-10',
        icon: 'size-4'
      },
      lg: {
        root: 'size-10',
        icon: 'size-5'
      }
    },
    fill: {
      true: {
        root: ''
      },
      false: {
        root: 'bg-transparent'
      }
    }
  },
  compoundVariants: [
    {
      hierarchy: 'primary',
      fill: false,
      className: {
        root: 'hover:bg-surfacecolor-tertiary focus:bg-surfacecolor-tertiary aria-disabled:opacity-60',
        icon: 'text-iconcolor-action'
      }
    },
    {
      hierarchy: ['primary'],
      fill: true,
      className: {
        root: 'bg-surfacecolor-action hover:bg-surfacecolor-action-hover focus:bg-surfacecolor-action-hover aria-disabled:bg-surfacecolor-disabled',
        icon: 'text-iconcolor-tertiary'
      }
    },
    {
      hierarchy: 'secondary',
      fill: false,
      className: {
        root: 'hover:bg-surfacecolor-tertiary focus:bg-surfacecolor-tertiary aria-disabled:opacity-60',
        icon: 'text-iconcolor-secondary'
      }
    },
    {
      hierarchy: ['secondary'],
      fill: true,
      className: {
        root: 'bg-surfacecolor-primary ring-1 ring-bordercolor-primary hover:bg-surfacecolor-secondary focus:bg-surfacecolor-secondary',
        icon: 'text-iconcolor-action group-aria-disabled/button:text-iconcolor-secondary'
      }
    },
    {
      hierarchy: ['destructive'],
      fill: false,
      className: {
        root: 'hover:bg-surfacecolor-error focus:bg-surfacecolor-error aria-disabled:opacity-60',
        icon: 'text-iconcolor-error'
      }
    },
    {
      hierarchy: ['destructive'],
      fill: true,
      className: {
        root: 'bg-surfacecolor-action-error hover:bg-surfacecolor-action-error-hover focus:bg-surfacecolor-action-error-hover aria-disabled:bg-surfacecolor-disabled',
        icon: 'text-iconcolor-tertiary'
      }
    }
  ],
  defaultVariants: {
    hierarchy: 'secondary',
    size: 'md',
    fill: false
  }
});
