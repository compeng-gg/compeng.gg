'use client';
 
import { createContext, useEffect, useState } from 'react';
 
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
  else {
    return (
      <JwtContext.Provider value={[jwt, setAndStoreJwt]}>
        {children}
      </JwtContext.Provider>
    );
  }
}
