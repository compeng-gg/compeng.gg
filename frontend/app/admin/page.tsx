'use client';

import { useContext, useEffect, useState } from 'react';

import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';

import LoginRequired from '@/app/lib/login-required';

import H1 from '@/app/ui/h1';
import H2 from '@/app/ui/h2';
import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';
import Table from '@/app/ui/table';

const userFields: [string, string][] = [
  ['id', 'ID'],
  ['username', 'Username'],
]

function AdminPage() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [users, setUsers] = useState<any[]>([]);

  const fetchData = async () => {
    try {
      const response = await fetchApi(jwt, setAndStoreJwt, "users/");
      const data = await response.json();
      setUsers(data);
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
        <H1>Admin</H1>
        <H2>Users</H2>
        <Table fields={userFields} data={users} />
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
