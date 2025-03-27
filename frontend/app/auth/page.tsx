'use client';

import { useContext, useEffect, useRef, useState } from 'react';

import { usePathname, useRouter, useSearchParams } from 'next/navigation';

import { fetchApi, fetchApiSingle } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';

import H1 from '@/app/ui/h1';

export default function Page() {
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const handleRef = useRef<Promise<void> | null>(null);
    const hasRunRef = useRef(false);
    const router = useRouter();
    const pathname = usePathname();
    const searchParams = useSearchParams();
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (hasRunRef.current) {
            return;
        }
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const action = sessionStorage.getItem('action');
        const provider = sessionStorage.getItem('provider');
        const next = sessionStorage.getItem('next');
        const stored_state = sessionStorage.getItem('state');

        const handle = async () => {
            if (code === null || state === null) {
                setError('Parameters missing');
                return;
            }
            if (action === null || provider === null || next === null || stored_state === null) {
                setError('Session state missing');
                return;
            }
            if (state !== stored_state) {
                setError('Cross-site request forgery detected');
                return;
            }
            try {
                if (action === 'auth') {
                    const response: Response = await fetchApiSingle(`${action}/${provider}/`, 'POST', {'code': code});
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
                        setError(data.detail);
                    }
                }
                else if (action === 'connect') {
                    const response: Response = await fetchApi(jwt, setAndStoreJwt, `${action}/${provider}/`, 'POST', {'code': code});
                    if (response.ok) {
                        if (next !== null) {
                            router.push(next);
                        }
                        else {
                            router.push('/');
                        }
                    }
                    else {
                        const data = await response.json();
                        setError(data.detail);
                    }
                }
            }
            catch (err) {
                setError('An unexpected error occurred');
            }
        };

        handleRef.current = handle();
        hasRunRef.current = true;

        return () => {
            if (handleRef.current) {
                handleRef.current.then(() => {
                    sessionStorage.removeItem('action');
                    sessionStorage.removeItem('provider');
                    sessionStorage.removeItem('next');
                    sessionStorage.removeItem('state');
                });
            }
        };
    }, [jwt, router, searchParams, setAndStoreJwt]);
    if (error === null) {
        return (
            <></>
        );
    }
    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-24">
            <H1>Auth</H1>
            <p className="text-red-500">{error}</p>
        </main>
    );
}
