'use client';

import { useEffect, useState, useContext } from 'react';
import { useParams } from 'next/navigation';
import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';
import Navbar from '@/app/components/navbar';

interface QuizAccommodation {
    user_id: number;
    username: string;
    visible_at_unix_timestamp: number;
    starts_at_unix_timestamp: number;
    ends_at_unix_timestamp: number;
}

export default function QuizAccommodationsPage() {
    const { courseSlug, offeringSlug, quizSlug } = useParams();
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [accommodations, setAccommodations] = useState<QuizAccommodation[]>([]);
    const [loading, setLoading] = useState(true);
    const [offeringName, setOfferingName] = useState('');
    const [quizTitle, setQuizTitle] = useState('');

    async function fetchAccommodations() {
        try {
            const res = await fetchApi(
                jwt,
                setAndStoreJwt,
                `quizzes/admin/${courseSlug}/${quizSlug}/accommodations/`,
                'GET'
            );
            if (!res.ok) {
                throw new Error('Failed to fetch accommodations');
            }
            const data = await res.json();
            setAccommodations(data.quiz_accommodations || []);
        } catch (error) {
            console.error('Failed to retrieve accommodations', error);
            setAccommodations([]);
        } finally {
            setLoading(false);
        }
    }

    async function fetchQuizInfo() {
        try {
            const res = await fetchApi(
                jwt,
                setAndStoreJwt,
                `quizzes/admin/${courseSlug}/${quizSlug}/`,
                'GET'
            );
            if (!res.ok) {
                throw new Error('Failed to fetch quiz details');
            }
            const data = await res.json();
            setOfferingName(data.offering_name);
            setQuizTitle(data.title);
        } catch (error) {
            console.error('Failed to retrieve quiz info', error);
        }
    }

    useEffect(() => {
        fetchAccommodations();
        fetchQuizInfo();
    }, [courseSlug, quizSlug, jwt, setAndStoreJwt]);

    if (loading) {
        return (
            <>
                <Navbar />
                <p>Loading accommodations...</p>
            </>
        );
    }

    return (
        <>
            <Navbar />
            <div style={{ padding: '20px' }}>
                <h1>{offeringName || 'ECE344 Fall 2024'}</h1>
                <h2>{quizTitle || 'Loading quiz...'}</h2>

                <h3>Accommodations</h3>
                {accommodations.length === 0 ? (
                    <p>No accommodations found.</p>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        {accommodations.map((item) => (
                            <div
                                key={item.user_id}
                                style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    padding: '10px',
                                    border: '1px solid #ccc',
                                    borderRadius: '8px',
                                    background: '#f9f9f9'
                                }}
                            >
                                <div>
                                    <p><strong>{item.username}</strong></p>
                                    <p>
                                        Visible At:{' '}
                                        {new Date(item.visible_at_unix_timestamp * 1000).toLocaleString()}
                                    </p>
                                    <p>
                                        Starts At:{' '}
                                        {new Date(item.starts_at_unix_timestamp * 1000).toLocaleString()}
                                    </p>
                                    <p>
                                        Ends At:{' '}
                                        {new Date(item.ends_at_unix_timestamp * 1000).toLocaleString()}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </>
    );
}
