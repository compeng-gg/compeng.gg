'use client';

import { useContext, useEffect, useState } from 'react';

import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';

import LoginRequired from '@/app/lib/login-required';
import Navbar from '@/app/ui/navbar';

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
      <main className="container mx-auto mt-4 p-4">
        <h1 className="mb-4 font-black text-5xl">Admin</h1>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
            </tr>
          </thead>
          <tbody>
          {users.map(user => <tr key={user.id}><td>{user.id}</td><td>{user.username}</td></tr>)}
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
