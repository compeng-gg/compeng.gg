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

function StaffAssignment() {
  const params = useParams<{ course_slug: string, assignment_slug: string }>();
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [data, setData] = useState<any>({});

  useEffect(() => {
    async function fetchLabs() {
      try {
        const response = await fetchApi(jwt, setAndStoreJwt, `courses/${params.course_slug}/staff/${params.assignment_slug}/`, "GET");
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
        <H2>{ data.name }</H2>
        <p>Students with submissions: { data.num_students_with_submissions }/{ data.num_students }</p>
        <table key="table" className="table-auto">
          <thead className="bg-slate-300 dark:bg-slate-700">
            <tr>
              <th className="text-left border border-slate-500 p-2 text-sm">Username</th>
              <th className="text-left border border-slate-500 p-2 text-sm">Repository</th>
              <th className="text-left border border-slate-500 p-2 text-center text-sm">Submissions</th>
              <th className="text-left border border-slate-500 p-2 text-sm">Accommodation</th>
            </tr>
          </thead>
          <tbody>
          {data.students.map((student: any, rowIndex: any) => (
            <tr key={rowIndex}>
              <td className="text-left border border-slate-500 p-2 text-sm" >{student.username}</td>
              <td className="text-left border border-slate-500 p-2 text-sm" >
                  {student.repository_name === "" ? (
                  <span className="text-red-500">Missing</span>
                  ) : (
                  <Link href={`${student.repository_url}`} className="text-blue-500 hover:underline">{ student.repository_name }</Link>
                  )}
              </td>
              <td className="text-left border border-slate-500 p-2 text-center text-sm" >{student.submissions}</td>
              <td className="text-left border border-slate-500 p-2 text-sm" >TODO</td>
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
      <StaffAssignment />
    </LoginRequired>
  );
}
