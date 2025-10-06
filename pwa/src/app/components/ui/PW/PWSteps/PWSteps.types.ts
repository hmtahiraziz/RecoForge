export interface PWStepsContextProps {
  step: number;
}

export interface PWStepsRootProps extends React.ComponentPropsWithRef<'div'> {
  step: number;
  asChild?: boolean;
}

export interface PWStepsItemProps extends React.ComponentPropsWithRef<'div'> {
  index: number;
  asChild?: boolean;
}
