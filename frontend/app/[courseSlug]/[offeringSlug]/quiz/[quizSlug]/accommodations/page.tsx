'use client';

import { useEffect, useState, useContext, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';
import Navbar from '@/app/ui/navbar';

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

    // Create modal states
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [username, setUsername] = useState('');
    const [visibleAt, setVisibleAt] = useState('');
    const [startsAt, setStartsAt] = useState('');
    const [endsAt, setEndsAt] = useState('');

    // Delete modal states
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [usernameToDelete, setUsernameToDelete] = useState('');

    const fetchAccommodations = useCallback(async () => {
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
    }, [
        jwt,
        setAndStoreJwt,
        courseSlug,
        quizSlug,
        setAccommodations,
        setLoading
    ]);    

    const fetchQuizInfo = useCallback(async () => {
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
    }, [
        jwt,
        setAndStoreJwt,
        courseSlug,
        quizSlug,
        setOfferingName,
        setQuizTitle
    ]);
    
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

    // Show the confirm-delete modal for a specific username
    function handleDeleteButtonClick(username: string) {
        setUsernameToDelete(username);
        setShowDeleteModal(true);
    }

    // Confirm deletion
    async function handleConfirmDelete() {
        try {
            const body = { username: usernameToDelete };
            const res = await fetchApi(
                jwt,
                setAndStoreJwt,
                `quizzes/admin/${courseSlug}/${quizSlug}/accommodation/delete/`,
                'DELETE',
                body
            );
            if (!res.ok) {
                throw new Error('Failed to delete accommodation');
            }
            setShowDeleteModal(false);
            setUsernameToDelete('');
            fetchAccommodations();
        } catch (error) {
            console.error('Error deleting accommodation:', error);
            alert('Failed to delete the accommodation. See console for details.');
        }
    }

    // Cancel deletion
    function handleCancelDelete() {
        setShowDeleteModal(false);
        setUsernameToDelete('');
    }

    useEffect(() => {
        fetchAccommodations();
        fetchQuizInfo();
    }, [courseSlug, quizSlug, jwt, setAndStoreJwt, fetchAccommodations, fetchQuizInfo]);

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

                {/* Button to open the "Create New Accommodation" modal */}
                <button
                    style={{ marginBottom: '20px' }}
                    onClick={() => setShowCreateModal(true)}
                >
                    Create New Accommodation
                </button>

                {/* Create modal */}
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
                                {/* Delete button */}
                                <button onClick={() => handleDeleteButtonClick(item.username)}>
                                    Delete
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Confirm-delete modal */}
            {showDeleteModal && (
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
                        <h2>Confirm Delete</h2>
                        <p>Are you sure you want to delete the accommodation for <strong>{usernameToDelete}</strong>?</p>
                        <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
                            <button onClick={handleConfirmDelete}>Yes</button>
                            <button onClick={handleCancelDelete}>No</button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
