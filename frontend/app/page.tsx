'use client';

import Link from 'next/link';
import LoginRequired from '@/app/lib/login-required';

import { createContext, useContext, useEffect, useRef, useState } from 'react';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';

import { MessageSeverity, PrimeReactProvider } from 'primereact/api';


import { Card } from 'primereact/card';

import DiscordButton from '@/app/ui/discord-button';
import GitHubButton from '@/app/ui/github-button';

import H1 from '@/app/ui/h1';
import H2 from '@/app/ui/h2';
import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';
import { Badge } from 'primereact/badge';
import { Button } from 'primereact/button';
import { Message, MessageProps } from 'primereact/message';
import { Messages } from 'primereact/messages';
import { useMountEffect } from 'primereact/hooks';
import { log } from 'console';
import PrimeWrapper from './ui/primeWrapper';
import { routeModule } from 'next/dist/build/templates/app-page';

function getBadgeForRole(role: string, size?: 'xlarge' | 'large') {

    const severity : string = (role == 'Student') ? 'info':'admin';
    return <Badge value={role} severity={severity} size={size}/>;
}

function getRoleFromOffering(offering) {
    const spIdx = offering.role.lastIndexOf(' ');
    return offering.role.substring(spIdx+1);
}

function getCourseCard(offering){
  
    console.log(offering.role);
    return (
        <Link href={`/${offering.course_slug}/${offering.offering_slug}/`} style={{maxWidth: '200px'}}>
            <PrimeWrapper>
                <Card title={offering.name} footer={getBadgeForRole(getRoleFromOffering(offering)) } />
            </PrimeWrapper>
        </Link>
    );

}


function Dashboard() {
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [isInitialized, setIsInitialized] = useState(false);
    const [username, setUsername] = useState('');
    const [failedChecks, setFailedChecks] = useState<any[]>([]);
    const [offerings, setOfferings] = useState<any[]>([]);

    useEffect(() => {
        let ignore = false;
    
        async function startFetching() {
            const res = await fetchApi(jwt, setAndStoreJwt, 'dashboard/', 'GET');
            const data = await res.json();
            if (!ignore) {
                console.log(data);
                setUsername(data.username);
                setOfferings(data.offerings);
                if ('failed-checks' in data) {
                    setFailedChecks(data['failed-checks']);
                }
                setIsInitialized(true);
            }
        }

        startFetching();

        return () => {
            ignore = true;
        };
    }, [setAndStoreJwt, jwt]);

    if (!isInitialized) {
        return (<></>);
    }




    const todos = [];
    if (failedChecks.length > 0) {
    //fix this
        todos.push(<H2>TODOs</H2>);
        var todoCards: any[] = [];
        if (failedChecks.includes('connect-discord')) {
            todoCards.push(
                <div className="text-blue p-4 rounded-lg shadow-lg bg-red-900 max-w-fit space-y-4">
                    <p>Please connect your Discord account to access repositories.</p>
                    <DiscordButton action="connect" />
                </div>);
        }
        if (failedChecks.includes('connect-github')) {
            todoCards.push(
                <div className="text-white p-4 rounded-lg shadow-lg bg-red-900 max-w-fit space-y-4">
                    <p>Please connect your GitHub account to access repositories.</p>
                    <GitHubButton action="connect" />
                </div>
            );
        }
        if (failedChecks.includes('join-github-organization')) {
            todoCards.push(
                <div className="text-white p-4 rounded-lg shadow-lg bg-red-900 max-w-fit space-y-4">
                    <p>Please join the GitHub organization. Click <a className="text-red-300" href="https://github.com/orgs/compeng-gg/invitation">here</a> to accept the invite.</p>
                </div>
            );
        }
        todos.push(<div className="flex flex-col gap-4">{...todoCards}</div>);
    }

  

    return (
        <>
            <Navbar />
            <Main>
                {/* {todos} */}
                <H2>Courses</H2>
                <ul>
                    <div style={{display: 'flex', flexDirection: 'row', flexWrap: 'wrap', gap: '10px'}}>
                        {offerings?.map((offering, i) =>
                            <div key={i}>
                                {getCourseCard(offering)}
                            </div>
                        )}
                    </div>
                </ul>
            </Main>
        </>
    );
}


export default function Page() {
    return (
        <LoginRequired>
            <PrimeReactProvider>
                <Dashboard />
            </PrimeReactProvider>
        </LoginRequired>
    );
}
