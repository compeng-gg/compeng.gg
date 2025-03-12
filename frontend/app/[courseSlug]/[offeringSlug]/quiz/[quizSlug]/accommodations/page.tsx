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
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [username, setUsername] = useState('');
    const [visibleAt, setVisibleAt] = useState('');
    const [startsAt, setStartsAt] = useState('');
    const [endsAt, setEndsAt] = useState('');

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

    async function handleCreate() {
        if (!username || !visibleAt || !startsAt || !endsAt) {
            alert('Please fill in all fields before creating an accommodation.');
            return;
        }

        try {
            const body = {
                username: username,
                visible_at: new Date(visibleAt).getTime() / 1000,
                starts_at: new Date(startsAt).getTime() / 1000,
                ends_at: new Date(endsAt).getTime() / 1000
            };

            const res = await fetchApi(
                jwt,
                setAndStoreJwt,
                `quizzes/admin/${courseSlug}/${quizSlug}/accommodation/create/`,
                'POST',
                body
            );
            if (!res.ok) {
                throw new Error('Failed to create accommodation');
            }

            setShowCreateModal(false);
            setUsername('');
            setVisibleAt('');
            setStartsAt('');
            setEndsAt('');
            fetchAccommodations();
        } catch (error) {
            console.error('Error creating accommodation:', error);
            alert('Failed to create the accommodation. See console for details.');
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

                {/* Button to open the modal, moved to the top */}
                <button
                    style={{ marginBottom: '20px' }}
                    onClick={() => setShowCreateModal(true)}
                >
                    Create New Accommodation
                </button>

                {showCreateModal && (
                    <div
                        style={{
                            position: 'fixed',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            backgroundColor: 'rgba(0, 0, 0, 0.5)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            zIndex: 999
                        }}
                    >
                        <div
                            style={{
                                backgroundColor: 'white',
                                padding: '20px',
                                borderRadius: '8px',
                                width: '300px'
                            }}
                        >
                            <h2>Create Accommodation</h2>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                                <input
                                    type="text"
                                    placeholder="Username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                                <label>Visible At</label>
                                <input
                                    type="datetime-local"
                                    value={visibleAt}
                                    onChange={(e) => setVisibleAt(e.target.value)}
                                />
                                <label>Starts At</label>
                                <input
                                    type="datetime-local"
                                    value={startsAt}
                                    onChange={(e) => setStartsAt(e.target.value)}
                                />
                                <label>Ends At</label>
                                <input
                                    type="datetime-local"
                                    value={endsAt}
                                    onChange={(e) => setEndsAt(e.target.value)}
                                />
                            </div>
                            <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
                                <button onClick={handleCreate}>Create</button>
                                <button onClick={() => setShowCreateModal(false)}>Cancel</button>
                            </div>
                        </div>
                    </div>
                )}

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
                                    <p>Visible At: {new Date(item.visible_at_unix_timestamp * 1000).toLocaleString()}</p>
                                    <p>Starts At: {new Date(item.starts_at_unix_timestamp * 1000).toLocaleString()}</p>
                                    <p>Ends At: {new Date(item.ends_at_unix_timestamp * 1000).toLocaleString()}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </>
    );
}
