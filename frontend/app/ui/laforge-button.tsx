'use client';

import { useContext } from 'react';
import { JwtContext } from '@/app/lib/jwt-provider';

import { usePathname } from 'next/navigation';

import Button from '@/app/ui/button';

function generateState() {
    return Math.random().toString(36).substring(6);
}

interface LaForgeButtonProps {
    action: 'auth' | 'connect';
}

const authRedirectUri = process.env.NEXT_PUBLIC_AUTH_REDIRECT_URI || 'http://localhost:3000/auth/';
const clientId = process.env.NEXT_PUBLIC_LAFORGE_CLIENT_ID || '';

function LaForgeButton({ action }: LaForgeButtonProps) {
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const pathname = usePathname();

    function handleClick(event: any) {
        const state = generateState();

        sessionStorage.setItem('action', action);
        sessionStorage.setItem('provider', 'laforge');
        sessionStorage.setItem('next', pathname);
        sessionStorage.setItem('state', state);

        const redirectUri = encodeURIComponent(authRedirectUri);
        const scope = 'read_user';
    
        window.location.href = `https://laforge.eecg.utoronto.ca/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}&state=${state}`;
    }

    const buttonText = action === 'auth' ? 'Login with UofT' : 'Connect with UofT';

    return (
        <Button kind="primary" onClick={handleClick}>
            {buttonText}
        </Button>
    );

}
export default LaForgeButton;

