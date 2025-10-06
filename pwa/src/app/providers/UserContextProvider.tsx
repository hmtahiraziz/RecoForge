'use client';

import { usePathname, useRouter } from 'next/navigation';
import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { retrieveCookie } from '../actions/cookies/cookies';

interface User {
  token: string;
  email: string;
  role: string;
}

interface UserContextType {
  user: User | null;
  setUser: (user: User | null) => void;
}

const UserContext = createContext<UserContextType | null>(null);

export const useUserContext = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUserContext must be used within a UserContextProvider');
  }
  return context;
};

export const UserContextProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const pathname = usePathname();
  const router = useRouter();

  const validateSession = useCallback(async () => {
    const user = await retrieveCookie('user');

    if (user) {
      setUser(user);
    }

    const isLoggedIn = user?.token;

    if (!isLoggedIn && pathname !== '/sign-in') {
      router.push('/sign-in');
    }

    if (isLoggedIn && pathname === '/sign-in') {
      router.push('/');
    }

    setIsLoading(false);
  }, [pathname, router]);

  useEffect(() => {
    validateSession();
  }, [pathname, router, validateSession]);

  return (
    <UserContext.Provider
      value={{
        user,
        setUser
      }}
    >
      {isLoading ? <div>Loading...</div> : children}
    </UserContext.Provider>
  );
};
