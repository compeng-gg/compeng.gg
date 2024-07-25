'use client';

import Link from 'next/link'
import Navbar from '@/app/ui/navbar';
import LogoutButton from '@/app/ui/logout-button';
import LoginRequired from '@/app/lib/login-required';

import H1 from '@/app/ui/h1';

import { useContext, useEffect, useState } from 'react';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';

function Dashboard() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [username, setUsername] = useState("");
  const [offerings, setOfferings] = useState([]);

  useEffect(() => {
    fetchApi(jwt, setAndStoreJwt, "users/self/")
    .then((res) => res.json())
    .then((data) => setUsername(data.username));
    fetchApi(jwt, setAndStoreJwt, "courses/offerings/")
    .then((res) => res.json())
    .then((data) => setOfferings(data));
  }, []);

  return (
    <>
      <Navbar />
      <main className="container mx-auto p-4 space-y-4">
        <H1>Dashboard</H1>
        <p className="mb-2">You&apos;re logged in as <span className="font-bold text-blue-500">{username}</span></p>
        <h2 className="font-bold text-2xl">Courses</h2>
        <ul>
          {offerings.map((offering, i) => <li key={i}>{offering}</li>)}
        </ul>
      </main>
    </>
  );
}

export default function Page() {
  return (
    <LoginRequired>
      <Dashboard />
    </LoginRequired>
  );
}
