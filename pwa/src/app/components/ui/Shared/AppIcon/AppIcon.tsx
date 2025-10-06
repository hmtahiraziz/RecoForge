import React, { forwardRef, Suspense, useMemo } from 'react';

import { cn } from '@/app/lib/utils/cn';

import { icons } from './useAppIcon';

import { AppIconProps, FallbackProps } from './AppIcon.types';

const Fallback = ({ className }: FallbackProps) => {
  return (
    <span aria-hidden="true" data-testid="icon-fallback" className={cn('invisible block size-6', className ?? '')} />
  );
};

export const AppIcon = forwardRef<SVGSVGElement, AppIconProps>(
  (props: AppIconProps, forwardRef: React.ForwardedRef<SVGSVGElement>) => {
    const { className, name, fallback, ...restProps } = props;

    const SvgIcon = useMemo(() => icons[name], [name]);

    const hasFallback = fallback !== undefined;

    if (!SvgIcon) {
      return null;
    }

    return (
      <Suspense fallback={hasFallback ? fallback : <Fallback className={className} />}>
        <SvgIcon {...restProps} ref={forwardRef} className={className} />
      </Suspense>
    );
  }
);

AppIcon.displayName = 'AppIcon';
