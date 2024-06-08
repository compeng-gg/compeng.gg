import { cookies } from "next/headers";
import Image from "next/image";
import LoginForm from '@/app/ui/login-form';
import withAuth from "@/app/lib/auth";

function Page({username}: {username: string}) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="mb-4 font-black text-5xl">CompEng.gg</h1>
      <p>You&apos;re logged in as <span className="font-bold text-blue-500">{username}</span>.</p>
    </main>
  );
}

export default withAuth(Page);
