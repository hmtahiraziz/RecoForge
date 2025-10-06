'use server';

import { cookies } from 'next/headers';

export async function storeCookie(name: string, value: any): Promise<void> {
  const cookieStore = await cookies();

  const stringifiedValue: string = JSON.stringify(value);

  cookieStore.set(name, stringifiedValue, {
    path: '/',
    maxAge: 3600, // 1 hour
    httpOnly: true,
    secure: true,
    sameSite: 'strict'
  });
}

export async function retrieveCookie(name: string): Promise<any> {
  const cookieStore = await cookies();

  const storedCookie = cookieStore.get(name);

  if (storedCookie) {
    if (storedCookie.value) {
      return JSON.parse(storedCookie.value);
    } else {
      return null;
    }
  } else {
    return null;
  }
}

export async function deleteCookie(name: string) {
  const cookieStore = await cookies();

  cookieStore.set(name, '', {
    path: '/',
    maxAge: 0,
    httpOnly: true,
    secure: true,
    sameSite: 'strict'
  });
}
