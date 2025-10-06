import { tv } from 'tailwind-variants';

export const PLRadioGroupStyles = tv({
  slots: {
    root: 'group/radio-group',
    item: 'group/radio-item peer/radio-item relative isolate flex size-8 shrink-0 items-center justify-center rounded-full outline-none disabled:opacity-50',
    indicator:
      'size-2 rounded-full bg-surfacecolor-action group-disabled/radio-item:bg-surfacecolor-disabled',
    effect:
      'absolute inset-0 -z-10 size-full rounded-full bg-transparent transition-colors duration-[200ms] ease-brand group-[:not(:disabled)]/radio-item:hover:bg-surfacecolor-tertiary group-[:not(:disabled)]/radio-item:group-focus-visible/radio-item:bg-surfacecolor-tertiary',
    circle:
      'pointer-events-none flex size-4 items-center justify-center rounded-full border border-solid border-bordercolor-primary bg-surfacecolor-primary shadow-sm group-disabled/radio-item:border-bordercolor-disabled group-disabled/radio-item:bg-surfacecolor-tertiary',
    label:
      'body-sm text-textcolor-primary group-disabled/radio-group:text-textcolor-primary/50 peer-disabled/radio-item:text-textcolor-primary/50',
  },
});
