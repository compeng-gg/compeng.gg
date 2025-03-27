'use client';

import { useParams } from 'next/navigation';
import { useContext, useEffect, useState } from 'react';

import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';
import H2 from '@/app/ui/h2';
import Assignment from '@/app/ui/assignment';

import LoginRequired from '@/app/lib/login-required';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';

function StaffAssignmentStudent() {
    const params = useParams<{ course_slug: string, assignment_slug: string, student_username: string }>();
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [data, setData] = useState<any>({});

    useEffect(() => {
        async function fetchAssignment() {
            try {
                const response = await fetchApi(jwt, setAndStoreJwt, `courses/${params.course_slug}/staff/${params.assignment_slug}/${params.student_username}/`, 'GET');
                const data = await response.json();
                setData(data);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }

        fetchAssignment();
    }, [params.course_slug, jwt, setAndStoreJwt, params.assignment_slug, params.student_username]);

    if (!data) {
        return (
            <>
                <Navbar />
                <Main>
                    <></>
                </Main>
            </>
        );
    }

    return (
        <>
            <Navbar />
            <Main>
                <Assignment assignment={data}/>
            </Main>
        </>
    );
}


export default function Page() {
    return (
        <LoginRequired>
            <StaffAssignmentStudent />
        </LoginRequired>
    );
}
