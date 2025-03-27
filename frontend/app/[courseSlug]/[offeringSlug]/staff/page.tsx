'use client';

import { useEffect, useState, useContext, Fragment } from 'react';
import { useParams } from 'next/navigation';

import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';
import H1 from '@/app/ui/h1';
import H2 from '@/app/ui/h2';
import H3 from '@/app/ui/h3';
import Link from 'next/link';

import LoginRequired from '@/app/lib/login-required';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';

function Staff() {
  const params = useParams<{ course_slug: string }>();
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [data, setData] = useState<any>({});

  useEffect(() => {
    async function fetchLabs() {
      try {
        const response = await fetchApi(jwt, setAndStoreJwt, `courses/${params.course_slug}/staff/`, "GET");
        const data = await response.json();
        setData(data);
      } catch (error) {
        console.error('Error fetching labs:', error);
      }
    }

    fetchLabs();
  }, [params.course_slug, jwt, setAndStoreJwt]);

  if (Object.keys(data).length === 0) {
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
        <H1>{ data.offering} Staff</H1>
        <H2>Assignments</H2>

            <table key="table" className="table-auto">
              <thead className="bg-slate-300 dark:bg-slate-700">
                <tr>
                  <th className="text-left border border-slate-500 p-2 text-sm">Name</th>
                  <th className="text-left border border-slate-500 p-2 text-sm">Due Date</th>
                </tr>
              </thead>
              <tbody>
                {data.assignments.map((assignment: any, index: any) => (
                  <tr key={index}>
                    <td className="text-left border border-slate-500 p-2 text-sm" >
                      <Link href={`/${params.course_slug}/staff/${assignment.slug}/`} className="text-blue-500 hover:underline">{ assignment.name }</Link>
                    </td>
                    <td className="text-left border border-slate-500 p-2 text-sm" >{`${new Date(assignment.due_date)}`}</td>
                  </tr>
                ))}
              </tbody>
            </table>
      </Main>
    </>
  );
}

export default function Page() {
  return (
    <LoginRequired>
      <Staff />
    </LoginRequired>
  );
}
