import { RadioGroupProps, RadioGroupItemProps } from '@radix-ui/react-radio-group';

import { LabelProps } from '@radix-ui/react-label';

export interface PLRadioGroupRootProps extends RadioGroupProps {
  isInvalid?: boolean;
}

export interface PLRadioGroupItemProps extends RadioGroupItemProps {
  classNames?: {
    root?: string;
    effect?: string;
    circle?: string;
    indicator?: string;
  };
}

export type PLRadioGroupLabelProps = LabelProps;
