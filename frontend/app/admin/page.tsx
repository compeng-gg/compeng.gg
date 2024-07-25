'use client';

import { useContext, useEffect, useState } from 'react';

import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';

import LoginRequired from '@/app/lib/login-required';
import Navbar from '@/app/ui/navbar';

import H1 from '@/app/ui/h1';

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
      <main className="container mx-auto p-4 space-y-4">
        <H1>Admin</H1>
        <table className="table-auto">
          <thead className="bg-slate-700">
            <tr>
              <th className="text-left border border-slate-500 p-2">ID</th>
              <th className="text-left border border-slate-500 p-2">Username</th>
            </tr>
          </thead>
          <tbody>
          {
            users.map(user =>
            <tr key={user.id}>
              <td className="text-left border border-slate-500 p-2">{user.id}</td>
              <td className="text-left border border-slate-500 p-2">{user.username}</td>
            </tr>)
          }
          </tbody>
        </table>
      </main>
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
