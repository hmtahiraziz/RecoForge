'use client';

import React from 'react';

import * as PopoverPrimitive from '@radix-ui/react-popover';

import { PLIconButton } from '@/app/components/ui/PL/PLIconButton';
import { useUserContext } from '@/app/providers/UserContextProvider';
import UserCircle from '@/app/icons/user-circle.svg';

import Link from 'next/link';
import Image from 'next/image';
import { PLButton } from '../PLButton/PLButton';
import { deleteCookie } from '@/app/actions/cookies/cookies';
import { useRouter } from 'next/navigation';

const LoggedInHeader = () => {
  const { user, setUser } = useUserContext();

  const router = useRouter();

  const handleSignOut = () => {
    deleteCookie('user');
    setUser(null);

    router.push('/sign-in');
  };

  if (!user?.email || !user?.role) {
    return null;
  }

  return (
    <header className="flex h-14 w-full items-center gap-0.5 bg-surfacecolor-primary fixed top-0 z-20 p-2 shadow-sm lg:h-16 lg:gap-4 lg:px-4 lg:py-3">
      <div className="pointer-events-none absolute inset-x-0 flex items-center justify-center lg:static lg:mr-[84px]">
        <Link href="/">
          <Image
            src={'/logo-paramount-horizontal.png'}
            width={120}
            height={32}
            alt="Paramount Liquor"
            className="pointer-events-auto h-6 w-[90px] lg:h-8 lg:w-[120px]"
          />
        </Link>
      </div>

      <PLButton hierarchy="secondary" className="shrink-0 ml-auto" size="lg" asChild>
        <Link href="/">Admin area</Link>
      </PLButton>

      <PLButton hierarchy="secondary" className="shrink-0" size="lg" asChild>
        <Link href="/preview">Preview</Link>
      </PLButton>

      <PopoverPrimitive.Root>
        <PopoverPrimitive.Trigger asChild>
          <PLIconButton className="shrink-0" size="lg" icon={<UserCircle />} />
        </PopoverPrimitive.Trigger>
        <PopoverPrimitive.Content
          onOpenAutoFocus={(event) => {
            event.preventDefault();
          }}
          align="end"
          sideOffset={4}
          className="z-1000 flex w-[288px] flex-col rounded-md border border-bordercolor-secondary bg-surfacecolor-primary p-2 shadow-lg outline-none"
        >
          <div className="flex flex-col">
            <p className="body-xs text-textcolor-primary">{user.email}</p>
            <p className="body-xs text-textcolor-secondary">{user.role}</p>
          </div>

          <div className="h-px w-full mb-4 mt-2 bg-bordercolor-secondary" />

          <PLButton hierarchy="secondary" className="w-full" onClick={handleSignOut}>
            Sign out
          </PLButton>
        </PopoverPrimitive.Content>
      </PopoverPrimitive.Root>
    </header>
  );
};

const LoggedOutHeader = () => {
  return (
    <header className="flex w-full items-center fixed top-0 gap-0.5 bg-surfacecolor-action p-2 shadow-sm h-16 z-20">
      <div className="pointer-events-none flex items-center justify-center">
        <Link href="/">
          <Image
            src="/pl-logo-signin.svg"
            width={120}
            height={32}
            alt="Paramount Liquor"
            className="pointer-events-auto h-10 w-[152px]"
          />
        </Link>
      </div>
    </header>
  );
};

export const PLHeader = () => {
  const { user } = useUserContext();

  const isUserLoggedIn = Boolean(user?.token);

  return isUserLoggedIn ? <LoggedInHeader /> : <LoggedOutHeader />;
};
