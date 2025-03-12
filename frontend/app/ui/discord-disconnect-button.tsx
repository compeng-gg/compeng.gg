'use client';

import { useContext } from 'react';

import { useRouter } from 'next/navigation';

import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';

import Button from '@/app/ui/button';

function DiscordDisconnectButton() {
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const router = useRouter();

    function handleClick(event: any) {
        fetchApi(jwt, setAndStoreJwt, 'disconnect/discord/', 'DELETE')
            .then((res) => { if (res.ok) { location.reload(); } });
    }

    return (
        <Button kind="secondary" onClick={handleClick}>
      Disconnect Discord
        </Button>
    );

}
export default DiscordDisconnectButton;
