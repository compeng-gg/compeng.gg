'use client';

import { useEffect, useState, useContext } from 'react';

import LoginRequired from '@/app/lib/login-required';
import H1 from '@/app/ui/h1';
import H2 from '@/app/ui/h2';
import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';
import Table from '@/app/ui/table';
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

const taskFields: [string, string][] = [
  ['id', 'ID'],
  ['status', 'Status'],
  ['grade', 'Grade'],
  ['repo', 'Repo'],
  ['commit', 'Commit'],
  ['received', 'Received'],
]

function Course({ params }: { params: { slug: string } }) {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [name, setName] = useState();
  const [labs, setLabs] = useState([] as Lab[]);

  useEffect(() => {
    async function fetchLabs() {
      try {
        const response = await fetchApi(jwt, setAndStoreJwt, `courses/${params.slug}/`, "GET");
        const data = await response.json();
        setName(data.name);
        setLabs(data.assignments);
      } catch (error) {
        console.error('Error fetching labs:', error);
      }
    }

    fetchLabs();
  }, [params.slug, jwt, setAndStoreJwt]);

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
        {labs.map((assignment) => (
          <div
            key={assignment.slug}
            className="bg-gray-900 shadow-md rounded-lg p-6 mb-6"
          >
            <h2 className="text-2xl font-semibold mb-2">{assignment.name}</h2>
            <p>
              Due: {`${new Date(assignment.due_date)}`}
            </p>
            <p className="mb-4">Grade: {assignment.grade}</p>

            <div className="border-t border-gray-500 pt-4">
              <h3 className="text-xl font-semibold mb-3">Pushes:</h3>
              {assignment.tasks.map((task: any) => (
                <div
                  key={task.id}
                  className="bg-gray-800 rounded-lg p-4 mb-4 shadow"
                >
                  <p>
                    <strong>Status:</strong> {task.status}
                  </p>
                  <p>
                    <strong>Grade:</strong> {task.grade}
                  </p>
                  <p>
                    <strong>Repo:</strong>{' '}
                    <a
                      href={`https://github.com/compeng-gg/${task.repo}`}
                      className="text-blue-500 hover:underline"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {task.repo}
                    </a>
                  </p>
                  <p>
                    <strong>Commit:</strong> {task.commit}
                  </p>
                  <p>
                    <strong>Received:</strong>{' '}
                    {`${new Date(task.received)}`}
                  </p>

                  <div className="border-t border-gray-500 mt-4 pt-2">
                    <h4 className="font-semibold mb-2">Test Results:</h4>
                    {task.result.tests.map((test:any, index:any) => (
                      <div
                        key={index}
                        className="bg-black p-3 rounded-lg shadow-sm mb-2"
                      >
                        <p>
                          <strong>Test:</strong> {test.name}
                        </p>
                        <p>
                          <strong>Weight:</strong> {test.weight}
                        </p>
                        <p>
                          <strong>Result:</strong>{' '}
                          <span
                            className={
                              test.result === 'OK'
                                ? 'text-green-600 font-semibold'
                                : 'text-red-600 font-semibold'
                            }
                          >
                            {test.result}
                          </span>
                        </p>
                        <p>
                          <strong>Duration:</strong> {test.duration.toFixed(2)}s
                        </p>
                        {test.stderr && (
                          <div className="bg-red-100 text-red-600 p-3 rounded mt-2">
                            <strong>Error:</strong> <pre>{test.stderr}</pre>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
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
