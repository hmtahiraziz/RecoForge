export interface PLMenuDefaultItemProps extends React.ComponentPropsWithRef<'button'> {
  selected?: boolean;
  description?: string;
  leadingIcon?: React.ReactNode;
  asChild?: boolean;
  classNames?: {
    root?: string;
    leadingIcon?: string;
    contentWrapper?: string;
    label?: string;
    description?: string;
    selectedIcon?: string;
  };
}
