'use client';

import { useContext } from 'react';

import { JwtContext } from '@/app/lib/jwt-provider';

import DiscordButton from '@/app/ui/discord-button';
import LoginForm from '@/app/ui/login-form';

export default function LoginRequired({
  children,
}: {
  children: React.ReactNode
}) {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);

  if (jwt === undefined) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <div>
          <h1 className="mb-4 font-black text-5xl">CompEng.gg</h1>
          <p>Already have an account?</p>
          <LoginForm />
          <DiscordButton action="auth" />
          <p>Need an account?</p>
          <button>GitHub</button>
        </div>
      </main>
    );
  }
  else {
    return (
      <>{children}</>
    );
  }
}
