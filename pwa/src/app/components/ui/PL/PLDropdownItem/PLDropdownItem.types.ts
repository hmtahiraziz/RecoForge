export interface PLDropdownItemProps extends React.ComponentPropsWithRef<'button'> {
  leadingIcon?: React.ReactElement;
  description?: string;
  caption?: string;
  selected?: boolean;
  asChild?: boolean;
  classNames?: {
    root?: string;
    mainWrapper?: string;
    labelCaptionWrapper?: string;
    label?: string;
    caption?: string;
    description?: string;
    selectedIcon?: string;
  };
}
