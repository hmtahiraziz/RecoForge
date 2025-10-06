export interface PLIconButtonProps extends React.ComponentPropsWithRef<'button'> {
  asChild?: boolean;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  hierarchy?: 'primary' | 'secondary' | 'destructive';
  fill?: boolean;
  icon?: React.ReactElement<HTMLElement>;
}
