'use client';

import { useContext, useEffect, useState } from 'react';

import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';

import LoginRequired from '@/app/lib/login-required';
import DiscordButton from '@/app/ui/discord-button';
import DiscordDisconnectButton from '@/app/ui/discord-disconnect-button';
import GitHubButton from '@/app/ui/github-button';
import Navbar from '@/app/ui/navbar';

import H1 from '@/app/ui/h1';

function SettingsPage() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [settings, setSettings] = useState<any>({});

  const fetchData = async () => {
    try {
      const response = await fetchApi(jwt, setAndStoreJwt, "settings/");
      const data = await response.json();
      setSettings(data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const discordElement = settings.discord ? (
    <>
      <p>Discord: {settings.discord}</p>
      <DiscordDisconnectButton />
    </>
  ) : (
    <div>
      <DiscordButton action='connect' />
    </div>
  );

  const githubElement = settings.github ? (
    <>
      <p>GitHub: {settings.github}</p>
    </>
  ) : (
    <div className="mt-4">
      <GitHubButton action='connect' />
    </div>
  );

  return (
    <>
      <Navbar />
      <main className="container mx-auto mt-4 p-4">
        <H1>Settings</H1>
        {discordElement}
        {githubElement}
      </main>
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
