'use client';

import { useContext, useEffect } from 'react';

import { useRouter, useSearchParams } from 'next/navigation'

import { fetchApiSingle } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';

export default function Page() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const provider = sessionStorage.getItem('provider');
    const next = sessionStorage.getItem('next');
    const stored_state = sessionStorage.getItem('state');

    const handle = async () => {
      if (state !== stored_state) {
        return;
      }
      if (provider === null) {
        return;
      }
      const response: Response = await fetchApiSingle(`auth/${provider}/`, {'code': code, 'state': state});
      if (response.ok) {
        const data = await response.json();
        setAndStoreJwt(data);
        if (next !== null) {
          router.push(next);
        }
        else {
          router.push('/');
        }
      }
      else {
        /* TODO: Display an error */
      }
    }

    handle();

    return () => {
      sessionStorage.removeItem('provider');
      sessionStorage.removeItem('next');
      sessionStorage.removeItem('state');
    }
  }, []);
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="mb-4 font-black text-5xl">Auth</h1>
    </main>
  );
}
