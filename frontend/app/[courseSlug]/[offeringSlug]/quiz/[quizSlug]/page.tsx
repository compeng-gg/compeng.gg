'use client';

import { useContext, useEffect, useState } from 'react';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';
import Navbar from '@/app/ui/navbar';
import LoginRequired from '@/app/lib/login-required';
import { useParams } from 'next/navigation';
import QuizWritingPage from './student_views/writing-view';
import ReleasedQuizView from './student_views/released-view';
import ViewOnlyQuizSubmission from './student_views/submission-view';

export default function Page() {
    const { courseSlug, quizSlug } = useParams<{ courseSlug: string; quizSlug: string }>();
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [quizInfo, setQuizInfo] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchQuizInfo() {
            try {
                const res = await fetchApi(
                    jwt,
                    setAndStoreJwt,
                    `quizzes/${courseSlug}/${quizSlug}/info/`,
                    'GET'
                );
                if (!res.ok) throw new Error('Failed to fetch quiz info');
                const data = await res.json();
                setQuizInfo({
                    ...data,
                    starts_at: new Date(data.starts_at * 1000),
                    ends_at: new Date(data.ends_at * 1000),
                    visible_at: new Date(data.visible_at * 1000),
                    release_at: new Date(data.release_at * 1000),
                });
            } catch (err) {
                console.error('Error fetching quiz info:', err);
            } finally {
                setLoading(false);
            }
        }

        fetchQuizInfo();
    }, [courseSlug, quizSlug, jwt, setAndStoreJwt]);

    if (loading) {
        return (
            <LoginRequired>
                <Navbar />
                <p>Loading quiz information...</p>
            </LoginRequired>
        );
    }

    if (!quizInfo) {
        return (
            <LoginRequired>
                <Navbar />
                <h3>Error: Could not load quiz information.</h3>
            </LoginRequired>
        );
    }

    const now = new Date();

    // ⏰ Quiz hasn't started yet
    if (now < quizInfo.starts_at) {
        return (
            <LoginRequired>
                <Navbar />
                <h3>This quiz starts at: {quizInfo.starts_at.toLocaleString()}</h3>
            </LoginRequired>
        );
    }

    // 📝 Writing Flow
    if (now >= quizInfo.starts_at && now <= quizInfo.ends_at) {
        // TODO: Replace this with: <QuizWritingPage quizInfo={quizInfo} />
        return (
            <LoginRequired>
                <Navbar />
                <QuizWritingPage courseSlug={courseSlug} quizSlug={quizSlug} />

            </LoginRequired>
        );
    }

    // ✅ Graded View
    if (now > quizInfo.release_at) {
        // TODO: Replace this with: <GradedQuizSubmissionView quizInfo={quizInfo} />
        return (
            <LoginRequired>
                <Navbar />
                <ReleasedQuizView />
            </LoginRequired>
        );
    }

    // 👁️ Viewable Submission (ungraded)
    if (quizInfo.viewable && now >= quizInfo.visible_at) {
        // TODO: Replace this with: <ViewableSubmissionView quizInfo={quizInfo} />
        return (
            <LoginRequired>
                <Navbar />
                <ViewOnlyQuizSubmission />
            </LoginRequired>
        );
    }

    // ❌ Not viewable yet
    return (
        <LoginRequired>
            <Navbar />
            <h3>This quiz has ended but is not viewable yet.</h3>
        </LoginRequired>
    );
}
