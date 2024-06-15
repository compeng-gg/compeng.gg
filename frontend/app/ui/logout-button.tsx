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
      className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
      onClick={handleClick}
    >
      Logout
    </button>
  )
}

export default LogoutButton
