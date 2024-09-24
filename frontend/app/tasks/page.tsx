'use client';

import { useContext, useEffect, useState } from 'react';

import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';

import LoginRequired from '@/app/lib/login-required';

import H1 from '@/app/ui/h1';
import H2 from '@/app/ui/h2';
import Main from '@/app/ui/main';
import Navbar from '@/app/components/navbar';
import Table from '@/app/ui/table';

const taskFields: [string, string][] = [
  ['id', 'ID'],
  ['status', 'Status'],
  ['grade', 'Grade'],
  ['repo', 'Repo'],
  ['commit', 'Commit'],
  ['received', 'Received'],
]

function AdminPage() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [tasks, setTasks] = useState<any[]>([]);

  const fetchData = async () => {
    try {
      const response = await fetchApi(jwt, setAndStoreJwt, "tasks/", "GET");
      const data = await response.json();
      const transformedData = data.map((item: any) => {
        const newItem: any = {
          id: item.id,
          status: item.status,
          grade: item.grade,
          repo: item.repo,
          commit: item.commit,
        };
        newItem["received"] = new Date(item.received).toString();
        return newItem;
      });
      setTasks(transformedData);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <>
      <Navbar />
      <Main>
        <H1>Tasks</H1>
        <Table fields={taskFields} data={tasks} />
      </Main>
    </>
  );

}

export default function Page() {
  return (
    <LoginRequired>
      <AdminPage />
    </LoginRequired>
  );
}
