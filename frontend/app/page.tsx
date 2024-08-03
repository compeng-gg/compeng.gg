'use client';

import Link from 'next/link'
import LogoutButton from '@/app/ui/logout-button';
import LoginRequired from '@/app/lib/login-required';

import { useContext, useEffect, useState } from 'react';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';

import H1 from '@/app/ui/h1';
import H2 from '@/app/ui/h2';
import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';

function Dashboard() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [username, setUsername] = useState("");
  const [offerings, setOfferings] = useState([]);

  useEffect(() => {
    fetchApi(jwt, setAndStoreJwt, "users/self/", "GET")
    .then((res) => res.json())
    .then((data) => setUsername(data.username));
    fetchApi(jwt, setAndStoreJwt, "courses/offerings/", "GET")
    .then((res) => res.json())
    .then((data) => setOfferings(data));
  }, []);

  return (
    <>
      <Navbar />
      <Main>
        <H1>Dashboard</H1>
        <H2>TODO</H2>
        <p>You&apos;re logged in as <span className="font-bold text-blue-500">{username}</span></p>
        <H2>Courses</H2>
        {offerings.map((offering, index) => (
        <button
          key={index}
          className="block bg-blue-500 text-white font-semibold py-2 px-4 rounded-md shadow-md hover:bg-blue-600 transition duration-200"
          // onClick={() => router.push(`/courses/${offering.id}`)}
        >
          {offering}
        </button>
      ))}
      </Main>
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
