import { cookies } from "next/headers";
import Image from "next/image";

import withAuth from "@/app/lib/auth";

import LoginForm from "@/app/ui/login-form";
import LogoutButton from "@/app/ui/logout-button";

function Page({username}: {username: string}) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="mb-4 font-black text-5xl">CompEng.gg</h1>
      <p className="mb-2">You&apos;re logged in as <span className="font-bold text-blue-500">{username}</span>.</p>
      <LogoutButton/>
    </main>
  );
}

export default withAuth(Page);
