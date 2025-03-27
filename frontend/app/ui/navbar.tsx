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

import { useContext, SyntheticEvent, useState, useEffect } from 'react';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';
import PrimeWrapper from './primeWrapper';
import { fetchUserName } from '@/app/lib/getUser';


export default function Navbar() {
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [username, setUserName] = useState('');
    const [offerings, setOfferings] = useState<any[]>([]);
  
    useEffect(() => {
        async function fetchOfferings() {
            try {
                const navbarRes = await fetchApi(jwt, setAndStoreJwt, 'navbar/', 'GET');
                const navbarData = await navbarRes.json();
                setOfferings(navbarData.offerings);
            } catch (error) {
                console.error('Error fetching offerings:', error);
            }
        }
        fetchOfferings();

        // Fetch username on component mount
        fetchUserName(jwt, setAndStoreJwt)
            .then((fetchedUserName) => setUserName(fetchedUserName))
            .catch((error) => console.error('Failed to fetch username:', error));
    }, [jwt, setAndStoreJwt]);

    //const router = useRouter();
    const startingIcon = (<Image src='/favicon.ico' width='25px' alt="favicon" />);
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
                    url: `/${o.course_slug}/${o.offering_slug}`
                };
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
    ];

    const avatar = (<Avatar label={username ?? '?'} />);

    return (
        <PrimeWrapper>
            <Menubar start={startingIcon} model={menuItems} end={avatar}/>
            <style jsx global>{`
        .p-submenu-list,
        .p-menuitem,
        .p-menuitem-content {
          z-index: 2000 !important;
        }
      `}</style>
        </PrimeWrapper>
    );
}