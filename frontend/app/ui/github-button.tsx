'use client';

import { useContext } from 'react';
import { JwtContext } from '@/app/lib/jwt-provider';

import { usePathname } from 'next/navigation';

import Button from '@/app/ui/button';

function generateState() {
  return Math.random().toString(36).substring(6);
}

interface GitHubButtonProps {
    action: 'auth' | 'connect';
}

const authRedirectUri = process.env.NEXT_PUBLIC_AUTH_REDIRECT_URI || 'http://localhost:3000/auth/';
const clientId = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID || '';

function GitHubButton({ action }: GitHubButtonProps) {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const pathname = usePathname()

  function handleClick(event: any) {
    const state = generateState();

    sessionStorage.setItem('action', action);
    sessionStorage.setItem('provider', 'github');
    sessionStorage.setItem('next', pathname);
    sessionStorage.setItem('state', state);

    const redirectUri = encodeURIComponent(authRedirectUri);
    
    window.location.href = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&state=${state}`;
  }

  const buttonText = action === 'auth' ? 'Login with GitHub' : 'Connect with GitHub';

  return (
    <Button kind="primary" onClick={handleClick}>
      {buttonText}
    </Button>
  )

}
export default GitHubButton;
