import React from 'react';

export function getSubtree(
  options: { asChild: boolean; children: React.ReactNode },
  content: React.ReactNode | ((children: React.ReactNode) => React.ReactNode)
) {
  const { asChild, children } = options;

  if (!asChild) return typeof content === 'function' ? content(children) : content;

  const firstChild = React.Children.only(children) as React.ReactElement;

  return React.cloneElement(firstChild, {
    // @ts-expect-error React.Children.only returns ReactNode but cloneElement expects ReactElement
    children: typeof content === 'function' ? content(firstChild.props.children) : content
  });
}
