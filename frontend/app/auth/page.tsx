'use client';

import { useContext, useEffect, useState } from 'react';

import { usePathname, useRouter, useSearchParams } from 'next/navigation'

import { fetchApiSingle } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';

export default function Page() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const provider = sessionStorage.getItem('provider');
    const next = sessionStorage.getItem('next');
    const stored_state = sessionStorage.getItem('state');

    const handle = async () => {
      if (code === null || state === null) {
        setError("Parameters missing");
        return;
      }
      if (provider === null || next === null || stored_state === null) {
        setError("Session state missing");
        return;
      }
      if (state !== stored_state) {
        setError("Cross-site request forgery detected")
        return;
      }
      const response: Response = await fetchApiSingle(`auth/${provider}/`, {'code': code, 'state': state});
      const data = await response.json();
      if (response.ok) {
        setAndStoreJwt(data);
        if (next !== null) {
          router.push(next);
        }
        else {
          router.push('/');
        }
      }
      else {
        setError(data.detail)
      }
    }

    handle();

    return () => {
      sessionStorage.removeItem('provider');
      sessionStorage.removeItem('next');
      sessionStorage.removeItem('state');
    }
  }, []);
  if (error === null) {
    return (
      <></>
    );
  }
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="mb-4 font-black text-5xl">Auth</h1>
      <p className="text-red-500">{error}</p>
    </main>
  );
}
