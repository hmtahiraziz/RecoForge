import type { SelectProps, SelectTriggerProps, SelectContentProps, SelectItemProps } from '@radix-ui/react-select';

export type PLSelectProviderProps = {
  options?: React.ReactElement[];
  setOptions?: React.Dispatch<React.SetStateAction<React.ReactElement[]>>;
  value?: SelectProps['value'];
  setValue?: React.Dispatch<React.SetStateAction<string | undefined>>;
  open?: SelectProps['open'];
  setOpen?: React.Dispatch<React.SetStateAction<boolean | undefined>>;
  disabled?: SelectProps['disabled'];
  isInvalid?: boolean;
  isClearable?: boolean;
  onClear?: () => void;
};

export interface PLSelectRootProps extends SelectProps {
  isInvalid?: boolean;
  isClearable?: boolean;
  onClear?: () => void;
}

export interface PLSelectTriggerProps extends SelectTriggerProps {
  placeholder?: React.ReactNode;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  leadingIcon?: React.ReactElement;
  trailingIcon?: React.ReactElement;
  isInvalid?: boolean;
  isClearable?: boolean;
  showInvalidIndicator?: boolean;
  showExpandIcon?: boolean;
  classNames?: {
    root?: string;
    cta?: string;
    leadingIcon?: string;
    trailingIcon?: string;
    expandIcon?: string;
    invalidIndicator?: string;
    clearable?: string;
    endContent?: string;
  };
}

export interface PLSelectContentProps extends SelectContentProps {
  viewportRef?: React.ForwardedRef<HTMLDivElement>;
  beforeViewportContent?: React.ReactNode;
  afterViewportContent?: React.ReactNode;
  classNames?: {
    root?: string;
    viewport?: string;
  };
}

export interface PLSelectDropdownItemProps extends SelectItemProps {
  leadingIcon?: React.ReactElement;
  description?: string;
  caption?: string;
}

export interface PLSelectMenuDefaultItemProps extends SelectItemProps {
  description?: string;
  leadingIcon?: React.ReactElement;
}
