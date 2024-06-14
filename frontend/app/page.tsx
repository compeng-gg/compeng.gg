'use client';

import LoginRequired from '@/app/lib/login-required';
import LogoutButton from '@/app/ui/logout-button';

import { useContext, useEffect, useState } from 'react';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';

function HomePage() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [username, setUsername] = useState("");

  useEffect(() => {
    fetchApi(jwt, setAndStoreJwt, "users/self/")
    .then((res) => res.json())
    .then((data) => setUsername(data.username));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="mb-4 font-black text-5xl">CompEng.gg</h1>
      <p className="mb-2">You&apos;re logged in as <span className="font-bold text-blue-500">{username}</span>.</p>
      <LogoutButton/>
    </main>
  );
}

export default function Page() {
  return (
    <LoginRequired>
      <HomePage />
    </LoginRequired>
  );
}
