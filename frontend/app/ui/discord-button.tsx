'use client';

import { useContext } from 'react';
import { JwtContext } from '@/app/lib/jwt-provider';

import { usePathname } from 'next/navigation';

function generateState() {
  return Math.random().toString(36).substring(6);
}

interface DiscordButtonProps {
    action: 'auth' | 'connect';
}

const authRedirectUri = process.env.NEXT_PUBLIC_AUTH_REDIRECT_URI || 'http://localhost:3000/auth/';
const clientId = process.env.NEXT_PUBLIC_DISCORD_CLIENT_ID || '1247897890806829086';

function DiscordButton({ action }: DiscordButtonProps) {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const pathname = usePathname()

  function handleClick(event: any) {
    const state = generateState();

    sessionStorage.setItem('action', action);
    sessionStorage.setItem('provider', 'discord');
    sessionStorage.setItem('next', pathname);
    sessionStorage.setItem('state', state);

    const redirectUri = encodeURIComponent(authRedirectUri);
    const scope = 'identify guilds.join';
    
    window.location.href = `https://discord.com/api/oauth2/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}&state=${state}`;
  }

  const buttonText = action === 'auth' ? 'Login with Discord' : 'Connect with Discord';

  return (
    <button
      className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
      onClick={handleClick}
    >
      {buttonText}
    </button>
  )

}
export default DiscordButton;
