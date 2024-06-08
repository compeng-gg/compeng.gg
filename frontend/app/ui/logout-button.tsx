'use client';

import { SyntheticEvent } from "react";
import { useRouter } from 'next/navigation';
import { fetchApi } from "@/app/lib/api-client";

function LogoutButton() {
  const router = useRouter();

  function handleClick(event: SyntheticEvent) {
    fetchApi("/auth/logout", {})
    .then((response) => response.json())
    .then((data) => console.log(data))
    .then(() => router.refresh());
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
