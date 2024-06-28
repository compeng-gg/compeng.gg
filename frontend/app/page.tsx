'use client';

import Link from 'next/link'
import Navbar from '@/app/ui/navbar';
import LogoutButton from '@/app/ui/logout-button';
import LoginRequired from '@/app/lib/login-required';

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
    <>
      <Navbar />
      <main className="container mx-auto mt-4 p-4">
        <h1 className="mb-4 font-black text-5xl">Dashboard</h1>
        <p className="mb-2">You&apos;re logged in as <span className="font-bold text-blue-500">{username}</span></p>
      </main>
    </>
  );
}

export default function Page() {
  return (
    <LoginRequired>
      <HomePage />
    </LoginRequired>
  );
}
