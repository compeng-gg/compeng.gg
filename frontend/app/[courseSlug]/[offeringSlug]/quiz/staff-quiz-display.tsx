import { Badge } from 'primereact/badge';
import { Card } from 'primereact/card';
import { differenceInMinutes } from 'date-fns';
import { Button } from 'primereact/button';
import Link from 'next/link';
import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';
import { useParams } from 'next/navigation';
import { useContext, useEffect, useState } from 'react';

export interface StaffQuizProps {
    name: string;
    courseSlug: string;
    offeringSlug: string;
    quizSlug: string;
    startTime: Date | null;
    endTime: Date | null;
    releaseTime: Date;
}

function StaffQuizDisplayBadges(props: StaffQuizProps) {
    const duration = props.startTime && props.endTime ? Math.abs(differenceInMinutes(props.endTime, props.startTime)) : 'N/A';

    return (
        <div style={{ position: 'relative' }}>
            <span></span>
            <div style={{ position: 'absolute', top: '10px', right: '10px', display: 'flex', gap: '8px' }}>
                <Badge value={`${duration} mins`} severity="secondary" />
            </div>
        </div>
    );
}

function StaffQuizButton({ quizProps }: { quizProps: StaffQuizProps }) {
    return (
        <div style={{ position: 'relative', display: 'flex', flexDirection: 'row-reverse' }}>
            <Link href={`/${quizProps.courseSlug}/${quizProps.offeringSlug}/quiz/${quizProps.quizSlug}/submissions/`}>
                <Button label="Grade Quiz" size="small" />
            </Link>
        </div>
    );
}

// function releaseNowButton({ quizProps }: { quizProps: StaffQuizProps }) {
    
// }

function ManageStudentQuizAccommodationsButton({ quizProps }: { quizProps: StaffQuizProps }) {
    return (
        <div style={{ position: 'relative', display: 'flex', flexDirection: 'row-reverse' }}>
            <Link href={`/${quizProps.courseSlug}/${quizProps.offeringSlug}/quiz/${quizProps.quizSlug}/accommodations/`}>
                <Button label="Manage Student Accommodations" size="small" />
            </Link>
        </div>
    );
}

export default function StaffQuizDisplay(props: StaffQuizProps) {
    if (!props.startTime || !props.endTime) {
        return <Card title={props.name} subTitle="Invalid quiz data" className="bg-gray-50 dark:white shadow-md rounded-lg" />;
    }

    const now = new Date();

    if (now <= props.startTime) {
        return UpcomingQuizDisplay(props);
    } else if (now <= props.endTime) {
        return OngoingQuizDisplay(props);
    } else {
        return PastQuizDisplay(props);
    }
}

//TODO: Fix logic on which buttons to show
function UpcomingQuizDisplay(props: StaffQuizProps) {

    const footer = () => {
        return (
            <div style={{display: 'flex', flexDirection: 'row', gap: '5px', justifyContent: 'flex-end'}}>
                <Link href={`/${props.courseSlug}/${props.offeringSlug}/quiz/edit/${props.quizSlug}/`}>
                    <Button label="Edit Quiz" size="small" />
                </Link>
                <StaffQuizButton quizProps={props} />
            </div>
        );
    };
    return (
        <Card
            header={<StaffQuizDisplayBadges {...props} />}
            footer={footer}
            title={props.name}
            subTitle={`Start Time: ${props.startTime}`}
            className="bg-gray-50 dark:white shadow-md rounded-lg"
        />
    );
}

function OngoingQuizDisplay(props: StaffQuizProps) {
    const footer = () => {
        return (
            <div style={{display: 'flex', flexDirection: 'row', gap: '5px', justifyContent: 'flex-end'}}>
                <Link href={`/${props.courseSlug}/${props.offeringSlug}/quiz/edit/${props.quizSlug}/`}>
                    <Button label="Edit Quiz" size="small" />
                </Link>
                <ManageStudentQuizAccommodationsButton quizProps={props} />
                <StaffQuizButton quizProps={props} />
            </div>
        );
    };

    return (
        <Card
            header={<StaffQuizDisplayBadges {...props} />}
            footer={footer}
            title={props.name}
            subTitle={`Started at: ${props.startTime}`}
            className="bg-green-50 dark:white shadow-md rounded-lg"
        />
    );
}

const ReleaseQuizNow = ({ quizProps }: { quizProps: StaffQuizProps }) => {
    const [jwt, setAndStoreJwt] = useContext(JwtContext);

    const handleReleaseQuiz = async () => {
        try {
            const res = await fetchApi(
                jwt,
                setAndStoreJwt,
                `quizzes/admin/${quizProps.courseSlug}/${quizProps.quizSlug}/release-now/`,
                'POST'
            );
            if (!res.ok) throw new Error('Failed to Release Quiz');
            console.log('Quiz released successfully!');
        } catch (error) {
            console.error('Failed to Release Quiz', error);
        }
    };

    return (
        <button onClick={handleReleaseQuiz}>
            Release Quiz Now
        </button>
    );
};

function ReleaseNowButton({ quizProps }: { quizProps: StaffQuizProps }) {
    const [releaseConfirmed, setReleaseConfirmed] = useState(false);

    async function handleReleaseQuiz() {
        try {
            await ReleaseQuizNow(quizProps);
            setReleaseConfirmed(true);
            setTimeout(() => setReleaseConfirmed(false), 3000); // Auto-close after 3 seconds
        } catch (error) {
            console.error('Failed to release quiz', error);
        }
    }

    // const now = new Date();
    // if (now >= quizProps.releaseTime) {
    //     return null; // Don't show the button if releaseTime has already passed
    // }

    return (
        <>
            <Button
                label="Release Now"
                size="small"
                severity="warning"
                onClick={handleReleaseQuiz}
            />
            {releaseConfirmed && (
                <div
                    style={{
                        position: 'fixed',
                        bottom: '70px',
                        right: '100px',
                        backgroundColor: '#28a745',
                        color: '#fff',
                        padding: '10px 15px',
                        borderRadius: '5px',
                        fontSize: '14px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)',
                    }}
                >
                    Quiz scores are now released!
                    <button
                        onClick={() => setReleaseConfirmed(false)}
                        style={{
                            background: 'none',
                            border: 'none',
                            color: '#fff',
                            fontSize: '14px',
                            cursor: 'pointer',
                        }}
                    >
                        ✖
                    </button>
                </div>
            )}
        </>
    );
}



function PastQuizDisplay(props: StaffQuizProps) {
    const footer = () => {
        console.log(props);
        return (
            <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'flex-end', gap: '5px' }}>
                {/* {new Date() < props.releaseTime && <ReleaseNowButton quizProps={props} />} */}
                <ReleaseNowButton quizProps={props} />
                <Link href={`/${props.courseSlug}/${props.offeringSlug}/quiz/edit/${props.quizSlug}/`}>
                    <Button label="Edit Quiz" size="small" />
                </Link>
                <StaffQuizButton quizProps={props} />
            </div>
        );
    };

    return (
        <Card
            header={<StaffQuizDisplayBadges {...props} />}
            footer={footer}
            title={props.name}
            subTitle={`Ended on: ${props.endTime ?? 'Unknown'}`}
            className="bg-gray-50 dark:white shadow-md rounded-lg"
        />
    );
}
