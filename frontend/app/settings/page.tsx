'use client';

import { useContext, useEffect, useState, useCallback } from 'react';

import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';

import LoginRequired from '@/app/lib/login-required';
import DiscordButton from '@/app/ui/discord-button';
import DiscordDisconnectButton from '@/app/ui/discord-disconnect-button';
import GitHubButton from '@/app/ui/github-button';
import GoogleButton from '@/app/ui/google-button';

import H1 from '@/app/ui/h1';
import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';

function SettingsPage() {
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [settings, setSettings] = useState<any>({});

    const fetchData = useCallback(async () => {
        try {
            const response = await fetchApi(jwt, setAndStoreJwt, 'settings/', 'GET');
            const data = await response.json();
            setSettings(data);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }, [jwt, setAndStoreJwt, setSettings]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const discordElement = settings.discord ? (
        <>
            <p>Discord: {settings.discord}</p>
        </>
    ) : (
        <div>
            <DiscordButton action='connect' />
        </div>
    );

    const githubElement = settings.github ? (
        <p>GitHub: {settings.github}</p>
    ) : (
        <div>
            <GitHubButton action='connect' />
        </div>
    );

    return (
        <>
            <Navbar />
            <Main>
                <H1>Settings</H1>
                {discordElement}
                {githubElement}
            </Main>
        </>
    );
}

export default function Page() {
    return (
        <LoginRequired>
            <SettingsPage />
        </LoginRequired>
    );
}
