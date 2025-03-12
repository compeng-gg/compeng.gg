'use client';

import { useContext, useState } from 'react';

import { JwtContext } from '@/app/lib/jwt-provider';

import Button from '@/app/ui/button';
import DiscordButton from '@/app/ui/discord-button';
import GitHubButton from '@/app/ui/github-button';
import LaForgeButton from '@/app/ui/laforge-button';
import LoginForm from '@/app/ui/login-form';

export default function LoginRequired({
    children,
}: {
  children: React.ReactNode
}) {
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [isClicked, setIsClicked] = useState(false);

    function handleClick() {
        setIsClicked(true);
    }

    if (jwt === undefined) {
        return (
            <main className="flex min-h-dvh items-center justify-center p-8">
                <div className="flex flex-col space-y-4">
                    <h1 className="font-black text-5xl">CompEng.gg</h1>
                    <LaForgeButton action="auth" />
                    {!isClicked ? (
                        <Button kind="secondary" onClick={handleClick}>Already have an account?</Button>
                    ) : (
                        <>
                            <LoginForm />
                            <DiscordButton action="auth" />
                            <GitHubButton action="auth" />
                        </>
                    )}
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
