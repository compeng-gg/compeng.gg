'use client';

import Link from 'next/link';
import LogoutButton from '@/app/ui/logout-button';
import { Menubar } from 'primereact/menubar';
import { MenuItem } from 'primereact/menuitem';
import { Image } from 'primereact/image';
import { Button } from 'primereact/button';
import { useRouter } from 'next/router';
import { PrimeIcons } from 'primereact/api';

import { Avatar } from 'primereact/avatar';

import { useContext, SyntheticEvent, useState, useEffect } from "react";
import { JwtContext } from '@/app/lib/jwt-provider';
import PrimeWrapper from './primeWrapper';
import { fetchUserName } from '@/app/lib/getUser';

export interface NavbarProps {
  offerings?: object[];
}

export default function Navbar(props: NavbarProps) {
  const { offerings} = props;
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [username, setUserName] = useState("");

    useEffect(() => {
        // Fetch username on component mount
        fetchUserName(jwt, setAndStoreJwt)
            .then((fetchedUserName) => setUserName(fetchedUserName))
            .catch((error) => console.error("Failed to fetch username:", error));
    }, [jwt, setAndStoreJwt]);

  //const router = useRouter();
  const startingIcon = (<Image src='/favicon.ico' width='25px' />)
  const menuItems : MenuItem[] = [
    { //home menu button
      label: 'Home',
      icon: PrimeIcons.HOME,
      url: '/'
    },
    { //courses button
      label: 'Courses',
      icon: 'pi pi-book',
      items: offerings?.map((o) => {
        return {
          label: o.name,
          url: `/${o.slug}/`
        }
      })
    },
    {
      label: 'Settings',
      icon: 'pi pi-cog',
      url: '/settings/'
    },
    {
      label: 'Logout',
      icon: 'pi pi-sign-out',
      command: () => {
        setAndStoreJwt(undefined);
      }
    },
  ]

  const avatar = (<Avatar label={username ?? '?'} />)

  return (
    <PrimeWrapper>
      <Menubar start={startingIcon} model={menuItems} end={avatar} />
    </PrimeWrapper>
  )

  return (
    <nav className="flex items-center justify-between flex-wrap bg-zinc-900 p-2">
      <div className="flex items-center flex-shrink-0 text-white mr-6">
        <Link href="/" className="font-black text-xl tracking-tight">CompEng.gg</Link>
      </div>
      <div className="block lg:hidden">
        <button className="flex items-center px-3 py-2 border rounded text-zinc-200 border-zinc-800 hover:text-white hover:border-white">
          <svg className="fill-current h-3 w-3" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><title>Menu</title><path d="M0 3h20v2H0V3zm0 6h20v2H0V9zm0 6h20v2H0v-2z"/></svg>
        </button>
      </div>
      <div className="w-full block flex-grow lg:flex lg:items-center lg:w-auto">
        <div className="text-sm lg:flex-grow">
          <Link href="/settings/" className="block mt-4 lg:inline-block lg:mt-0 text-zinc-100 hover:text-white mr-4">
            Settings
          </Link>
        </div>
        <div>
          <LogoutButton />
        </div>
      </div>
    </nav>
  );
}