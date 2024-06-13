'use client';
 
import { createContext, useEffect, useState } from 'react';
 
import LoginForm from '@/app/ui/login-form';
 
export const JwtContext = createContext<any>([undefined, undefined]);

function getLocalStorage(key: string): any {
  const storedValue = localStorage.getItem(key);
  return storedValue ? JSON.parse(storedValue) : undefined;
}

function setLocalStorage(key: string, value: any) {
  localStorage.setItem(key, JSON.stringify(value));
}

export default function JwtProvider({
  children,
}: {
  children: React.ReactNode
}) {
  const [jwt, setJwt] = useState(undefined);
  const [isInitialized, setIsInitialized] = useState(false);

  const setAndStoreJwt = (newJwt: any) => {
    if (newJwt === undefined) {
      localStorage.removeItem("jwt");
    }
    else {
      setLocalStorage("jwt", newJwt);
    }
    setJwt(newJwt);
  };

  useEffect(() => {
    setJwt(getLocalStorage("jwt"));
    setIsInitialized(true);
  }, []);

  if (!isInitialized) {
    return (<></>);
  }
  else if (jwt === undefined) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <div>
          <h1 className="mb-4 font-black text-5xl">CompEng.gg</h1>
          <JwtContext.Provider value={[jwt, setAndStoreJwt]}>
            <LoginForm />
          </JwtContext.Provider>
        </div>
      </main>
    );
  }
  else {
    return (
      <JwtContext.Provider value={[jwt, setAndStoreJwt]}>
        {children}
      </JwtContext.Provider>
    );
  }
}
