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
  const [isInitialized, setIsInitialized] = useState(false);
  const [username, setUsername] = useState("");
  const [offerings, setOfferings] = useState<any[]>([]);

  useEffect(() => {
    let ignore = false;

    async function startFetching() {
      const res = await fetchApi(jwt, setAndStoreJwt, "dashboard/", "GET");
      const data = await res.json();
      if (!ignore) {
        setUsername(data.username);
        setOfferings(data.offerings);
        setIsInitialized(true);
      }
    }

    startFetching();

    return () => {
      ignore = true;
    };
  }, []);

  if (!isInitialized) {
    return (<></>);
  }

  return (
    <>
      <Navbar />
      <Main>
        <H1>Dashboard</H1>
        <H2>TODO</H2>
        <p>You&apos;re logged in as <span className="font-bold text-blue-500">{username}</span></p>
        <H2>Courses</H2>
        <ul>
          {offerings.map((offering, i) =>
            <li key={i}>
               <Link href={`/${offering.slug}/`} className="text-blue-500 hover:underline">
                 {offering.name}
               </Link>
            </li>
          )}
        </ul>
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
