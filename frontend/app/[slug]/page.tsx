'use client';

import { useEffect, useState, useContext } from 'react';

import LoginRequired from '@/app/lib/login-required';
import H1 from '@/app/ui/h1';
import H2 from '@/app/ui/h2';
import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';
import Link from 'next/link';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';

interface Lab {
  name: string;
  slug: string;
  due_date: Date;
}

function Course({ params }: { params: { slug: string } }) {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [labs, setLabs] = useState([] as Lab[]);

  useEffect(() => {
    async function fetchLabs() {
      try {
        const response = await fetchApi(jwt, setAndStoreJwt, `courses/${params.slug}/`, "GET");
        const data = await response.json();
        setLabs(data);
      } catch (error) {
        console.error('Error fetching labs:', error);
      }
    }

    fetchLabs();
  }, [params.slug, jwt, setAndStoreJwt]);

  if (labs.length === 0) {
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
        <H1>{params.slug}</H1>
        <ul className="mt-2">
          {labs.length > 0 ? (
            labs.map((lab, index) => {
              const isFutureLab = new Date(lab.start) > new Date();
              return (
                <li key={index} className="mb-4">
                  <Link
                    href={`/${params.slug}/${lab.slug}`}
                    className={`block p-6 rounded-md shadow-md transition duration-200 ${
                      isFutureLab
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-blue-500 hover:bg-blue-600 text-white'
                    }`}
                    style={{
                      pointerEvents: isFutureLab ? 'none' : 'auto',
                    }}
                  >
                    <div className="flex justify-between items-center">
                      <span className="text-2xl font-bold">{lab.name}</span>
                      <span className="text-sm text-right">{`Due: ${new Date(lab.due_date)}`}</span>
                    </div>
                  </Link>
                </li>
              );
            })
          ) : (
            <p>No labs available for this course.</p>
          )}
        </ul>
      </Main>
    </>
  );
}

export default function Page({ params }: { params: { slug: string } }) {
  return (
    <LoginRequired>
      <Course params={params} />
    </LoginRequired>
  );
}
