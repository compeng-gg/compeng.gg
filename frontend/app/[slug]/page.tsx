'use client';

import { useEffect, useState, useContext } from 'react';

import LoginRequired from '@/app/lib/login-required';
import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';
import Link from 'next/link';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';

interface Lab {
  name: string;
  slug: string;
  start: Date;
  end: Date;
}


function Course({ params }: { params: { slug: string } }) {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [labs, setLabs] = useState([] as Lab[]);

  useEffect(() => {
    async function fetchLabs() {
      try {
        const response = await fetchApi(jwt, setAndStoreJwt, `courses/labs/`, "GET", params);  // I expect this path to be added to urls.py in the backend. I'm paasing it params as data so that it knows the labs of which course to return.
        if (response.ok) {
          const data = await response.json();
          setLabs(data); // Assuming data is an array of labs
        } else {
          console.error('Failed to fetch labs:', response.statusText);
        }
      } catch (error) {
        console.error('Error fetching labs:', error);
        // this is just for testing since I don't have a backend to test with
        /*
        setLabs([{
          name: 'Lab 1',
          slug: 'lab-1',
          start: new Date(),
          end: new Date(),
        },
        {
          name: 'Lab 2',
          slug: 'lab-2',
          start: new Date('2025-09-01'),
          end: new Date('2025-09-30'),
        },]);
        */
      }
    }

    fetchLabs();
  }, [params.slug, jwt, setAndStoreJwt]);

  return (
    <>
      <Navbar />
      <Main>
        <h2 className="text-xl font-bold mt-4">Labs for {params.slug}</h2>
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
                      <span className="text-sm text-right">{`Start: ${new Date(lab.start).toLocaleDateString()}`}</span>
                    </div>
                    <div className="text-sm text-right text-gray-200">
                      {`End: ${new Date(lab.end).toLocaleDateString()}`}
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
