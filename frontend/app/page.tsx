'use client';

import Link from 'next/link'
import LoginRequired from '@/app/lib/login-required';

import { useContext, useEffect, useState } from 'react';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';

import DiscordButton from '@/app/ui/discord-button';
import GitHubButton from '@/app/ui/github-button';

import H1 from '@/app/ui/h1';
import H2 from '@/app/ui/h2';
import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';
import Courses from '@/app/ui/courses';


function Dashboard() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [isInitialized, setIsInitialized] = useState(false);
  const [username, setUsername] = useState("");
  const [failedChecks, setFailedChecks] = useState<any[]>([]);
  const [offerings, setOfferings] = useState<any[]>([]);

  useEffect(() => {
    let ignore = false;

    async function startFetching() {
      const res = await fetchApi(jwt, setAndStoreJwt, "dashboard/", "GET");
      const data = await res.json();
      if (!ignore) {
        console.log(data)
        setUsername(data.username);
        setOfferings(data.offerings);
        if ("failed-checks" in data) {
          setFailedChecks(data['failed-checks'])
        }
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

  var todos: any[] = [];
  if (failedChecks.length > 0) {
    todos.push(<H2>TODOs</H2>);
    var todoCards: any[] = [];
    if (failedChecks.includes('connect-discord')) {
      todoCards.push(
        <div className="p-4 rounded-xl shadow-lg bg-red-900 max-w-fit space-y-4 transition transform active:scale-95">
          <p>Please connect your Discord account to access discussion.</p>
          <DiscordButton action="connect" />
        </div>
      );
    }
    if (failedChecks.includes('connect-github')) {
      todoCards.push(
        <div className="p-4 rounded-xl shadow-lg bg-red-900 max-w-fit space-y-4 transition transform active:scale-95">
          <p>Please connect your GitHub account to access repositories.</p>
          <GitHubButton action="connect"/>
        </div>
      );
    }
    todos.push(<div className="flex flex-col gap-4">{...todoCards}</div>);
  }

  return (
    <>
      <Navbar />
      <Main>
        <H1>
          <Link href="/">Dashboard</Link>
        </H1>
        <p className='text-1xl'>You&apos;re logged in as <span className="font-bold text-blue-500">{username}</span></p>
        {...todos}
        <Link href='/courses' className="m-4">
        <Courses/>
        </Link>
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
