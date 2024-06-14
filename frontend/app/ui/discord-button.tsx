'use client';

import { useContext } from 'react';
import { fetchApi, fetchApiSingle } from "@/app/lib/api";
import { JwtContext } from '@/app/lib/jwt-provider';

import { usePathname } from 'next/navigation';

function DiscordButton() {

  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const pathname = usePathname()

  function handleClick(event: any) {
    sessionStorage.setItem("provider", "discord");
    sessionStorage.setItem("next", pathname);
    window.location.href = 'https://discord.com/oauth2/authorize?client_id=963564393050832936&redirect_uri=http://localhost:3000/oauth2/&response_type=code&scope=identify+guilds.join+identify'
    /*
    fetchApiSingle("/auth/login/discord/")
    .then((res) => res.json())
    .then((data) => console.log("Test: ", data));
    */
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
