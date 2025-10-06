// In your cn.ts file
import clsx from 'clsx';
import { extendTailwindMerge } from 'tailwind-merge';

const customTwMerge = extendTailwindMerge({
  extend: {
    classGroups: {
      'font-size': ['text-heading-sm', 'text-body-xs', 'text-heading-h4']
    }
  }
});

export function cn(...classNames: string[] | undefined[] | null[] | unknown[]) {
  return customTwMerge(clsx(classNames));
}
