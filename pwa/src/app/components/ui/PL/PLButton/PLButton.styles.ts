import { tv } from 'tailwind-variants';

export const PLButtonStyles = tv({
  slots: {
    root: 'group/button cursor-pointer relative inline-flex items-center justify-center rounded-md text-center outline-none ring-inset transition duration-[200ms] ease-brand focus:ring-2 focus:ring-focuscolor-primary aria-disabled:pointer-events-none aria-disabled:cursor-not-allowed',
    icon: ''
  },
  variants: {
    hierarchy: {
      primary: {
        root: 'bg-surfacecolor-action text-textcolor-tertiary hover:bg-surfacecolor-action-hover hover:focus:bg-surfacecolor-action aria-disabled:bg-surfacecolor-disabled',
        icon: 'text-iconcolor-tertiary'
      },
      secondary: {
        root: 'bg-surfacecolor-primary text-textcolor-primary ring-1 ring-bordercolor-primary hover:bg-surfacecolor-secondary aria-disabled:text-textcolor-disabled',
        icon: 'text-iconcolor-action group-aria-disabled/button:text-iconcolor-secondary'
      },
      tertiary: {
        root: 'bg-transparent text-textcolor-tertiary ring-1 ring-bordercolor-tertiary hover:bg-surfacecolor-primary/[.12] hover:focus:bg-transparent aria-disabled:opacity-40',
        icon: 'text-iconcolor-tertiary'
      },
      link: {
        root: 'bg-transparent text-textcolor-action underline hover:text-textcolor-action-hover hover:focus:text-textcolor-action aria-disabled:text-textcolor-disabled',
        icon: 'text-iconcolor-action group-hover/button:text-iconcolor-action-hover group-hover/button:group-focus/button:text-iconcolor-action group-aria-disabled/button:text-iconcolor-secondary'
      },
      'link-tertiary': {
        root: 'bg-transparent text-textcolor-tertiary underline hover:opacity-80 focus:opacity-80 aria-disabled:text-textcolor-disabled',
        icon: 'text-iconcolor-tertiary group-aria-disabled/button:text-iconcolor-secondary group-data-[loading]/button:group-aria-disabled/button:text-iconcolor-tertiary'
      },
      'destructive-primary': {
        root: 'bg-surfacecolor-action-error text-textcolor-tertiary hover:bg-surfacecolor-action-error-hover hover:focus:bg-surfacecolor-action-error aria-disabled:bg-surfacecolor-disabled',
        icon: 'text-iconcolor-tertiary'
      },
      'destructive-secondary': {
        root: 'bg-surfacecolor-primary text-textcolor-primary ring-1 ring-bordercolor-primary hover:bg-surfacecolor-error aria-disabled:bg-surfacecolor-primary aria-disabled:text-textcolor-disabled',
        icon: 'text-iconcolor-error group-aria-disabled/button:text-iconcolor-secondary'
      },
      'destructive-link': {
        root: 'bg-transparent text-textcolor-error hover:text-surfacecolor-action-error-hover hover:focus:text-textcolor-error aria-disabled:text-textcolor-disabled',
        icon: 'text-iconcolor-error group-hover/button:text-surfacecolor-action-error-hover group-hover/button:group-focus/button:text-iconcolor-error group-aria-disabled/button:text-iconcolor-secondary'
      },
      checkout: {
        root: 'bg-surfacecolor-highlight text-textcolor-tertiary hover:bg-surfacecolor-highlight-hover hover:focus:bg-surfacecolor-highlight aria-disabled:bg-surfacecolor-disabled',
        icon: 'text-iconcolor-tertiary'
      }
    },
    size: {
      xs: {
        root: 'body-xxs h-6 gap-1 px-1.5',
        icon: 'size-3'
      },
      sm: {
        root: 'body-xs h-8 gap-1.5 px-3',
        icon: 'size-4'
      },
      md: {
        root: 'body-sm h-10 gap-2 px-4',
        icon: 'size-4'
      },
      lg: {
        root: 'body-md h-10 gap-2 px-4',
        icon: 'size-5'
      }
    },
    isIconOnly: {
      true: {
        root: 'p-0'
      }
    }
  },
  compoundVariants: [
    {
      hierarchy: ['link', 'link-tertiary', 'destructive-link'],
      className: {
        root: 'w-fit px-0'
      }
    },
    {
      hierarchy: ['primary', 'secondary', 'tertiary', 'destructive-primary', 'destructive-secondary', 'checkout'],
      isIconOnly: true,
      size: 'xs',
      className: {
        root: 'size-6'
      }
    },
    {
      hierarchy: ['primary', 'secondary', 'tertiary', 'destructive-primary', 'destructive-secondary', 'checkout'],
      isIconOnly: true,
      size: 'sm',
      className: {
        root: 'size-8'
      }
    },
    {
      hierarchy: ['primary', 'secondary', 'tertiary', 'destructive-primary', 'destructive-secondary', 'checkout'],
      isIconOnly: true,
      size: ['md', 'lg'],
      className: {
        root: 'size-10'
      }
    }
  ]
});
