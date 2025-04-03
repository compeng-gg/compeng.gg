'use client';

import { useEffect, useState, useContext } from 'react';

import LoginRequired from '@/app/lib/login-required';
import H1 from '@/app/ui/h1';
import H2 from '@/app/ui/h2';
import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';
import Table from '@/app/ui/table';
import Link from 'next/link';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';
import { TabMenu } from 'primereact/tabmenu';
import StudentView from '../../studentView/student-view';
import { Card } from 'primereact/card';
import StaffView from '../../staffView/staff-view';

export interface Lab {
  name: string;
  slug: string;
  due_date: Date;
  grade: number;
  tasks: any;
}

function getRoleEnum(role: string) {
    const spIdx = role.lastIndexOf(' ');
    return role.substring(spIdx+1);
}

const leaderboardFields: [string, string][] = [
    ['id', 'ID'],
    ['speedup', 'Speedup'],
];

function Course({ params }: { params: { courseSlug: string, offeringSlug: string } }) {
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [name, setName] = useState('');
    const [labs, setLabs] = useState([] as Lab[]);
    const [role, setRole] = useState<string | undefined>(undefined);
    const [teamsEnabled, setTeamsEnabled] = useState<boolean>(false);

    useEffect(() => {
        async function fetchLabs() {
            try {
                //To do: include role in this API
                const response = await fetchApi(jwt, setAndStoreJwt, `courses/${params.courseSlug}/`, 'GET');
                const data = await response.json();
                setName(data.name);
                setLabs(data.assignments);
                setRole(getRoleEnum(data.role));
                setTeamsEnabled(data.teams_enabled);
            } catch (error) {
                console.error('Error fetching labs:', error);
            }
        }

        fetchLabs();
    }, [params.courseSlug, jwt, setAndStoreJwt]);

    return (
        <>
            <Navbar />
            <Card>
                {(role == 'Student')
                    ? <StudentView courseName={name} labs={labs} courseSlug={params.courseSlug} offeringSlug={params.offeringSlug} teamsEnabled={teamsEnabled}/>
                    : <StaffView courseName={name} labs={labs} courseSlug={params.courseSlug} offeringSlug={params.offeringSlug}/>}
            </Card>
        </>
    );
}

export default function Page({ params }: { params: { courseSlug: string, offeringSlug: string } }) {
    return (
        <LoginRequired>
            <Course params={params} />
        </LoginRequired>
    );
}
