'use client';

import { useContext, SyntheticEvent } from "react";

import { JwtContext } from '@/app/lib/jwt-provider';

function LogoutButton() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);

  function handleClick(event: SyntheticEvent) {
    setAndStoreJwt(undefined);
  }

  return (
    <button
      className="inline-block text-sm px-4 py-2 leading-none border rounded text-white border-zinc-800 hover:border-transparent hover:text-red-400 hover:bg-black mt-4 lg:mt-0"
      // className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
      onClick={handleClick}
    >
      Logout
    </button>
  )
}

export default LogoutButton
