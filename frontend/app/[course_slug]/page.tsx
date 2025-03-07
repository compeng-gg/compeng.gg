'use client';

import { useEffect, useState, useContext } from 'react';
import { useParams } from 'next/navigation';

import LoginRequired from '@/app/lib/login-required';
import H1 from '@/app/ui/h1';
import Assignment from '@/app/ui/assignment';
import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';
import Link from 'next/link';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';

interface Lab {
  name: string;
  slug: string;
  due_date: Date;
  grade: number;
  tasks: any;
}

function Course() {
  const params = useParams<{ course_slug: string }>();
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [name, setName] = useState();
  const [labs, setLabs] = useState([] as Lab[]);
  const [data, setData] = useState<any>({});

  useEffect(() => {
    async function fetchLabs() {
      try {
        const response = await fetchApi(jwt, setAndStoreJwt, `courses/${params.course_slug}/`, "GET");
        const data = await response.json();
        setName(data.name);
        setLabs(data.assignments);
        setData(data);
      } catch (error) {
        console.error('Error fetching labs:', error);
      }
    }

    fetchLabs();
  }, [params.course_slug, jwt, setAndStoreJwt]);

  if (!name) {
    return (
      <>
        <Navbar />
        <Main>
          <></>
        </Main>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <Main>
        <H1>{name}</H1>
        { data.is_staff && <p><Link href={`/${params.course_slug}/staff`} className="text-yellow-500 hover:underline">Staff</Link></p>}

        { labs.map((assignment) => <Assignment key={assignment.slug} assignment={assignment}/>) }
      </Main>
    </>
  );
}

export default function Page() {
  return (
    <LoginRequired>
      <Course />
    </LoginRequired>
  );
}
