import { VariantProps } from 'tailwind-variants';
import { PLButtonStyles } from '@/app/components/ui/PL/PLButton/PLButton.styles';

export type PLActionGroupVariants = VariantProps<typeof PLButtonStyles>;

export interface PLButtonProps extends React.ComponentPropsWithRef<'button'> {
  asChild?: boolean;
  size?: PLActionGroupVariants['size'];
  hierarchy?: PLActionGroupVariants['hierarchy'];
  isLoading?: boolean;
  icon?: React.ReactElement<HTMLElement>;
  leadingIcon?: React.ReactElement<HTMLElement>;
  trailingIcon?: React.ReactElement<HTMLElement>;
}
