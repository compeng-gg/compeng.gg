'use client';

import { useContext } from 'react';
import { JwtContext } from '@/app/lib/jwt-provider';

import { usePathname } from 'next/navigation';

function generateState() {
  return Math.random().toString(36).substring(6);
}

interface GitHubButtonProps {
    action: 'auth' | 'connect';
}

const authRedirectUri = process.env.NEXT_PUBLIC_AUTH_REDIRECT_URI || 'http://localhost:3000/auth/';

function GitHubButton({ action }: GitHubButtonProps) {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const pathname = usePathname()

  function handleClick(event: any) {
    const state = generateState();

    sessionStorage.setItem('action', action);
    sessionStorage.setItem('provider', 'github');
    sessionStorage.setItem('next', pathname);
    sessionStorage.setItem('state', state);

    const clientId = 'Iv23lilBO4UQqz4hOmpL';
    const redirectUri = encodeURIComponent(authRedirectUri);
    
    window.location.href = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&state=${state}`;
  }

  const buttonText = action === 'auth' ? 'Login with GitHub' : 'Connect with GitHub';

  return (
    <button
      className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
      onClick={handleClick}
    >
      {buttonText}
    </button>
  )

}
export default GitHubButton;
