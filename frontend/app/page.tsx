import { cookies } from "next/headers";
import Image from "next/image";
import LoginForm from '@/app/ui/login-form';

async function checkAuthenticated() {
  const cookieStore = cookies();
  const csrfToken = cookieStore.get("csrftoken");
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v0';
  const response = await fetch(apiUrl + '/auth/session',
        {
            mode: "cors",
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": process.env.NEXT_PUBLIC_ORIGIN || "http://localhost:3000",
                "X-CSRFToken": csrfToken?.value || '',
            },
            credentials: "include",
        }
  )
  if (!response.ok) {
    return false;
  }
  return true;
}

export default async function Page() {
  const isAuthenticated = await checkAuthenticated();

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div>
        <h1 className="mb-3 font-black text-5xl">CompEng.gg</h1>
        <div>
          The user is <b>{isAuthenticated ? 'currently' : 'not'}</b> logged in.
        </div>
        <LoginForm />
      </div>
    </main>
  );
}
