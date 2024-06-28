'use client';

import { useContext } from 'react';

import { useRouter } from 'next/navigation'

import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';

function DiscordDisconnectButton() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const router = useRouter();

  function handleClick(event: any) {
    fetchApi(jwt, setAndStoreJwt, "disconnect/discord/")
    .then((res) => { if (res.ok) { location.reload(); } })
  }

  return (
    <button
      className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
      onClick={handleClick}
    >
      Disconnect Discord
    </button>
  )

}
export default DiscordDisconnectButton;
