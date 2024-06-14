'use client';

import { useContext } from 'react';
import { fetchApi, fetchApiSingle } from "@/app/lib/api";
import { JwtContext } from '@/app/lib/jwt-provider';

import { usePathname } from 'next/navigation';

function generateState() {
  return Math.random().toString(36).substring(7);
}

function DiscordButton() {

  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const pathname = usePathname()

  function handleClick(event: any) {
    const state = generateState();

    sessionStorage.setItem("provider", "discord");
    sessionStorage.setItem("next", pathname);
    sessionStorage.setItem("state", state);

    const clientId = '963564393050832936';
    const redirectUri = encodeURIComponent('http://localhost:3000/auth/');
    const scope = 'identify guilds.join';
    
    window.location.href = `https://discord.com/api/oauth2/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}&state=${state}`;
  }

  return (
    <button
      className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
      onClick={handleClick}
    >
      Login with Discord
    </button>
  )

}
export default DiscordButton;
