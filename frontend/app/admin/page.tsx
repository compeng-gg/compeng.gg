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

const userFields: [string, string][] = [
  ['id', 'ID'],
  ['username', 'Username'],
  ['email', 'Email'],
  ['first_name', 'First Name'],
  ['last_name', 'Last Name'],
  ['discord', 'Discord'],
  ['github', 'GitHub'],
]

function AdminPage() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [users, setUsers] = useState<any[]>([]);

  const fetchData = async () => {
    try {
      const response = await fetchApi(jwt, setAndStoreJwt, "users/", "GET");
      const data = await response.json();
      const transformedData = data.map((item: any) => {
        const newItem: any = {
          id: item.id,
          username: item.username,
          email: item.email,
          first_name: item.first_name,
          last_name: item.last_name,
        };
        item.social_auth.forEach((auth: any) => {
          newItem[auth.provider] = auth.uid;
        });
        return newItem;
      });
      setUsers(transformedData);
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
