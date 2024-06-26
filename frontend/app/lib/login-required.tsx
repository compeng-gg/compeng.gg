'use client';

import { useContext } from 'react';

import { JwtContext } from '@/app/lib/jwt-provider';

import DiscordButton from '@/app/ui/discord-button';
import GitHubButton from '@/app/ui/github-button';
import LoginForm from '@/app/ui/login-form';

export default function LoginRequired({
  children,
}: {
  children: React.ReactNode
}) {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);

  if (jwt === undefined) {
    return (
      <main className="flex min-h-dvh items-center justify-center p-8">
        <div>
          <h1 className="mb-4 font-black text-5xl">CompEng.gg</h1>
          <p className="mb-2">Already have an account?</p>
          <LoginForm />
          <div className="flex flex-col items-center justify-center">
            <DiscordButton action="auth" />
            <div className="mt-4"></div>
            <GitHubButton action="auth" />
          </div>
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
