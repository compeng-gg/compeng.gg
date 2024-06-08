import { cookies } from "next/headers";

import LoginForm from '@/app/ui/login-form';

function getSession(): Promise<any> {
  const cookieStore = cookies();
  const allCookies = cookieStore.getAll();
  const cookieString = allCookies.map(cookie => `${cookie.name}=${cookie.value}`).join('; ');
  const csrfToken = cookieStore.get("csrftoken");
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v0';
  return fetch(apiUrl + '/auth/session', {
    mode: "cors",
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": process.env.NEXT_PUBLIC_ORIGIN || "http://localhost:3000",
      "X-CSRFToken": csrfToken?.value || '',
      Cookie: cookieString,
    },
    credentials: "include",
  })
  .then(response => response.json())
  .then(data => data)
  .catch(error => {return {"is_authenticated": false};});
}

export default function withAuth(Component: any) {
  return async function Wrapper(props: any) {
    const session = await getSession();
    if (session.is_authenticated) {
        const username = session.username;
        return (<Component {...props} username={username} />);
    }
    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <div>
            <h1 className="mb-4 font-black text-5xl">CompEng.gg</h1>
            <LoginForm />
        </div>
        </main>
    );
  }
}
