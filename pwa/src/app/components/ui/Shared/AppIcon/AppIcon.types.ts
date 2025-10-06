import { ICON_NAMES } from './useAppIcon';

export type ImportFunctionProps = () => Promise<{ ReactComponent: React.FC<React.SVGProps<SVGSVGElement>> }>;

export type IconNameType = keyof typeof ICON_NAMES;

export interface AppIconProps extends React.ComponentPropsWithRef<'svg'> {
  name: IconNameType;
  fallback?: React.ReactNode;
}

export interface FallbackProps {
  className?: string;
}
