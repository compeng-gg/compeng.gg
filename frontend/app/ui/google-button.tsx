'use client';

import { useContext } from 'react';
import { JwtContext } from '@/app/lib/jwt-provider';

import { usePathname } from 'next/navigation';

import Button from '@/app/ui/button';

function generateState() {
  return Math.random().toString(36).substring(6);
}

interface GoogleButtonProps {
    action: 'auth' | 'connect';
}

const authRedirectUri = process.env.NEXT_PUBLIC_AUTH_REDIRECT_URI || 'http://localhost:3000/auth/';
const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || '';

function GoogleButton({ action }: GoogleButtonProps) {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const pathname = usePathname()

  function handleClick(event: any) {
    const state = generateState();

    sessionStorage.setItem('action', action);
    sessionStorage.setItem('provider', 'google');
    sessionStorage.setItem('next', pathname);
    sessionStorage.setItem('state', state);

    // const scope = 'openid email profile https://www.googleapis.com/auth/youtube.readonly';
    const scope = 'email https://www.googleapis.com/auth/youtube';

    const redirectUri = encodeURIComponent(authRedirectUri);
    
    window.location.href = `https://accounts.google.com/o/oauth2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}&state=${state}`;
  }

  const buttonText = action === 'auth' ? 'Login with Google' : 'Connect with Google';

  return (
    <Button kind="primary" onClick={handleClick}>
      {buttonText}
    </Button>
  )

}
export default GoogleButton;
