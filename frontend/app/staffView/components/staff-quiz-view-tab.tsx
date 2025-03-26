import TextEditor from '@/app/[courseSlug]/[offeringSlug]/quiz/components/text-editor';
import StaffQuizDisplay, { StaffQuizProps } from '@/app/[courseSlug]/[offeringSlug]/quiz/staff-quiz-display';
import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';
import { Button } from 'primereact/button';
import { Calendar } from 'primereact/calendar';
import { InputText } from 'primereact/inputtext';
import { useContext, useEffect, useState } from 'react';

export interface StaffQuizViewProps {
    courseSlug: string;
    offeringSlug: string;
}

export default function StaffQuizViewTab(props: StaffQuizViewProps) {
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [quizzes, setQuizzes] = useState<StaffQuizProps[]>([]);
    const [loading, setLoading] = useState(true);

    const [showModal, setShowModal] = useState(false);

    // Form state for creating a new quiz
    const [title, setTitle] = useState('');
    const [slug, setSlug] = useState('');
    const [visibleAt, setVisibleAt] = useState('');
    const [startsAt, setStartsAt] = useState('');
    const [endsAt, setEndsAt] = useState('');
    const [releaseAt, setReleaseAt] = useState('');
    const [githubRepository, setGithubRepository] = useState('');
    const [formError, setFormError] = useState('');

    async function fetchQuizzes() {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `quizzes/list/${props.courseSlug}`, 'GET');
            const data = await res.json();

            if (!Array.isArray(data) || data.length === 0) {
                setQuizzes([]);
            } else {
                const retQuizzes: StaffQuizProps[] = data.map((quiz: any) => ({
                    name: quiz.title,
                    quizSlug: quiz.slug,
                    courseSlug: props.courseSlug,
                    offeringSlug: props.offeringSlug,
                    startTime: quiz.start_unix_timestamp
                        ? new Date(quiz.start_unix_timestamp * 1000)
                        : null,
                    endTime: quiz.end_unix_timestamp
                        ? new Date(quiz.end_unix_timestamp * 1000)
                        : null,
                    releaseTime: quiz.releases_unix_timestamp
                        ? new Date(quiz.release_unix_timestamp * 1000)
                        : new Date(),
                }));
                setQuizzes(retQuizzes);
            }
        } catch (error) {
            console.error('Failed to retrieve quizzes', error);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchQuizzes();
    }, [props.courseSlug]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setFormError('');

        // Convert datetime-local values to Unix timestamps (seconds)
        const visibleTimestamp = Math.floor(new Date(visibleAt).getTime() / 1000);
        const startTimestamp = Math.floor(new Date(startsAt).getTime() / 1000);
        const endTimestamp = Math.floor(new Date(endsAt).getTime() / 1000);
        const releaseTimestamp = Math.floor(new Date(releaseAt).getTime() / 1000);

        // Validate start < end
        if (startTimestamp >= endTimestamp) {
            setFormError('Start time must be before end time.');
            return;
        }

        // Validate GitHub repo format
        const githubRegex = /^[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+$/;
        if (!githubRegex.test(githubRepository)) {
            setFormError('GitHub repository must be in the format \'user_name/repo_name\'.');
            return;
        }

        const payload = {
            title,
            slug,
            visible_at_timestamp: visibleTimestamp,
            releases_at_timestamp: releaseTimestamp,
            starts_at_timestamp: startTimestamp,
            ends_at_timestamp: endTimestamp,
            github_repository: githubRepository,
        };

        try {
            const res = await fetchApi(
                jwt,
                setAndStoreJwt,
                `quizzes/admin/${props.courseSlug}/create/`,
                'POST',
                payload
            );
            if (res.ok) {
                // Refresh quiz list and close modal on success
                fetchQuizzes();
                setShowModal(false);

                // Clear form
                setTitle('');
                setSlug('');
                setVisibleAt('');
                setStartsAt('');
                setEndsAt('');
                setGithubRepository('');
            } else {
                const errorData = await res.json();
                setFormError(errorData.detail || 'Error creating quiz.');
            }
        } catch (error) {
            console.error('Error creating quiz:', error);
            setFormError('An unexpected error occurred.');
        }
    };

    if (loading) return <p>Loading quizzes...</p>;
    // if (quizzes.length === 0) return <p>No quizzes available.</p>;

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', width: '100%', marginTop: '10px' }}>
            {/* 
                Match existing button style. 
                Replace `btn btn-primary` with your actual classes if different. 
            */}
            <div style={{display: 'flex', flexDirection: 'row', justifyContent: 'flex-end'}}>
                <Button icon="pi pi-plus" label="Create New Quiz" onClick={() => setShowModal(true)}/>
            </div>
            {quizzes.map((quiz) => (
                <StaffQuizDisplay key={quiz.quizSlug} {...quiz} />
            ))}

            {showModal && (
                <div className="modal-backdrop">
                    <div className="modal-content">
                        <h2 style={{ marginTop: 0 }}>Create New Quiz</h2>
                        <form onSubmit={handleSubmit}>
                            <div>
                                <label htmlFor="quiz-title">Title:</label>
                                <input
                                    id="quiz-title"
                                    type="text"
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    required
                                    title="Enter a short, descriptive title for the quiz."
                                />
                            </div>
                            <div>
                                <label htmlFor="quiz-slug">Slug:</label>
                                <input
                                    id="quiz-slug"
                                    type="text"
                                    value={slug}
                                    onChange={(e) => setSlug(e.target.value)}
                                    required
                                    title="Enter a URL-friendly slug (e.g., midterm-quiz)."
                                />
                            </div>
                            <div>
                                <label htmlFor="quiz-visibleAt">Visible At:</label>
                                <input
                                    id="quiz-visibleAt"
                                    type="datetime-local"
                                    value={visibleAt}
                                    onChange={(e) => setVisibleAt(e.target.value)}
                                    required
                                    title="Date and time when the quiz becomes visible to students."
                                />
                            </div>
                            <div>
                                <label htmlFor="quiz-startsAt">Starts At:</label>
                                <input
                                    id="quiz-startsAt"
                                    type="datetime-local"
                                    value={startsAt}
                                    onChange={(e) => setStartsAt(e.target.value)}
                                    required
                                    title="Date and time when the quiz officially starts."
                                />
                            </div>
                            <div>
                                <label htmlFor="quiz-endsAt">Ends At:</label>
                                <input
                                    id="quiz-endsAt"
                                    type="datetime-local"
                                    value={endsAt}
                                    onChange={(e) => setEndsAt(e.target.value)}
                                    required
                                    title="Date and time when the quiz ends."
                                />
                            </div>
                            <div>
                                <label htmlFor="quiz-releaseAt">Release Scores At:</label>
                                <input
                                    id="quiz-releaseAt"
                                    type="datetime-local"
                                    value={releaseAt}
                                    onChange={(e) => setReleaseAt(e.target.value)}
                                    required
                                    title="Date and time when the quiz score gets released."
                                />
                            </div>
                            <div>
                                <label htmlFor="quiz-githubRepo">GitHub Repository:</label>
                                <input
                                    id="quiz-githubRepo"
                                    type="text"
                                    value={githubRepository}
                                    onChange={(e) => setGithubRepository(e.target.value)}
                                    placeholder="user_name/repo_name"
                                    required
                                    title="Enter the GitHub repo in the format 'user_name/repo_name'."
                                />
                            </div>
                            {formError && <p style={{ color: 'red' }}>{formError}</p>}
                            <div style={{ display: 'flex', marginTop: '10px', gap: '5px' }}>
                                {/* Match your existing button classes here as well */}
                                <Button label="Submit" type="submit" size="small"/>
                                <Button label="Cancel" onClick={() => setShowModal(false)} severity="danger" size="small"/>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Inline (or module) styles for modal/backdrop */}
            <style jsx>{`
                .modal-backdrop {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-color: rgba(0, 0, 0, 0.5);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 9999; /* ensure it’s on top */
                }
                .modal-content {
                    background-color: #fff;
                    border-radius: 8px;
                    padding: 20px;
                    max-width: 500px;
                    width: 90%;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
                }
                .modal-content form > div {
                    margin-bottom: 1rem;
                }
                .modal-content label {
                    display: block;
                    margin-bottom: 0.3rem;
                    font-weight: 600;
                }
                .modal-content input {
                    width: 100%;
                    padding: 0.5rem;
                    border-radius: 4px;
                    border: 1px solid #ccc;
                }
            `}</style>
        </div>
    );
}
