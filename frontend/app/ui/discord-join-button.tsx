'use client';

import { useContext, useState } from 'react';

import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';

import Button from '@/app/ui/button';

function DiscordJoinButton() {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [isJoined, setIsJoined] = useState<Boolean>(false);

  function handleClick(event: any) {
    fetchApi(jwt, setAndStoreJwt, "join-discord/", "GET")
    .then((res) => { if (res.ok) { setIsJoined(true) } })
  }

  if (isJoined) {
    return (<></>)
  }

  return (
    <Button kind="secondary" onClick={handleClick}>
      Join Discord
    </Button>
  )

}
export default DiscordJoinButton;
