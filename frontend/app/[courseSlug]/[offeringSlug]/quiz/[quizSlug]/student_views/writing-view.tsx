'use client';

import Navbar from '@/app/ui/navbar';
import LoginRequired from '@/app/lib/login-required';
import { useContext, useEffect, useState, useCallback } from 'react';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';
import { getQuestionDataFromRaw } from '../../quiz-utilities';
import { QuestionDisplay } from '../../question-display';
import { Badge } from 'primereact/badge';
import { Button } from 'primereact/button';
import { confirmDialog, ConfirmDialog } from 'primereact/confirmdialog';

import { QuestionData, QuestionState, CodeQuestionData, QuestionProps } from '../../question-models';
import { QuizProps } from '../../quiz-display';

export default function WritingQuizView({ offeringSlug, courseSlug, quizSlug }: { offeringSlug: string; courseSlug: string; quizSlug: string }) {
    
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [quiz, setQuiz] = useState<QuizProps | undefined>(undefined);
    const [loaded, setLoaded] = useState(false);
    const [questionData, setQuestionData] = useState<QuestionData[]>([]);
    const [questionStates, setQuestionStates] = useState<QuestionState[]>([]);

    const fetchQuiz = useCallback(async () => {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `${courseSlug}/quiz/${quizSlug}`, 'GET');
            const data = await res.json();
    
            const retQuiz: QuizProps = {
                startTime: new Date(data.start_unix_timestamp * 1000),
                endTime: new Date(data.end_unix_timestamp * 1000),
                quizSlug,
                name: data.title,
                courseSlug,
                releaseTime: new Date(data.release_unix_timestamp * 1000),
                grade: data.grade,
                offeringSlug: offeringSlug
            };
    
            setQuiz(retQuiz);
    
            const qData = data.questions.map((rawData: any, idx: number) =>
                getQuestionDataFromRaw(rawData, quizSlug, courseSlug)
            );
            setQuestionData(qData);
    
            const states = qData.map((q : QuestionData,  idx: number) => ({
                value: getStartingStateValue(q, data.questions[idx]) as string | number | string[] | undefined,
                setValue: (newValue : any) =>
                    setQuestionStates((prev) =>
                        prev.map((s, i) => (i === idx ? { ...s, value: newValue } : s))
                    )
            }));
            setQuestionStates(states);
        } catch (error) {
            console.error('Failed to retrieve quiz', error);
        }
    }, [
        jwt,
        setAndStoreJwt,
        courseSlug,
        quizSlug,
        setQuiz,
        setQuestionData,
        setQuestionStates,
        offeringSlug,
    ]);    

    async function submitQuiz() {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `${courseSlug}/quiz/${quizSlug}/complete/`, 'POST', {});
            if (!res.ok) throw new Error('Failed to submit quiz');
            window.location.href += 'complete/';
        } catch {
            console.error('Failed to submit quiz');
        }
    }

    useEffect(() => {
        if (!loaded) {
            fetchQuiz();
            setLoaded(true);
        }
    }, [loaded, fetchQuiz]);

    if (!loaded || !quiz) {
        return (
            <LoginRequired>
                <Navbar />
                <h3 style={{ color: 'yellow' }}>{`Loading quiz ${quizSlug}...`}</h3>
            </LoginRequired>
        );
    }

    return (
        <>
            <QuizWritingHeader quiz={quiz} submitDialog={() =>
                confirmDialog({
                    message: 'Are you sure you want to submit your answers?',
                    header: 'Confirmation',
                    icon: 'pi pi-exclamation-triangle',
                    accept: submitQuiz,
                    reject: () => {}
                })
            } />
            <ConfirmDialog />
            <div style={{ display: 'flex', gap: '10px', width: '100%', flexDirection: 'column' }}>
                {questionStates.map((state, idx) => {
                    const validatedQuestionData = {
                        ...questionData[idx],
                        state,
                        idx,
                    } as QuestionProps;
                    return (
                        <QuestionDisplay
                            key = {idx}
                            {...validatedQuestionData}
                        />
                    )
                })}
            </div>
        </>
    );
}

function getStartingStateValue(questionData: QuestionData, rawData: any): any {
    switch (questionData.questionType) {
    case 'CODE':
        return rawData.solution ?? (questionData as CodeQuestionData).starterCode ?? '';
    case 'SELECT':
        return rawData.selected_answer_index ?? -1;
    case 'TEXT':
        return rawData.response ?? '';
    case 'MULTI_SELECT':
        return rawData.selected_answer_indices ?? [];
    default:
        throw new Error(`Unsupported question type: ${JSON.stringify(questionData)}`);
    }
}

function QuizWritingHeader({ quiz, submitDialog }: { quiz: QuizProps; submitDialog: () => void }) {
    return (
        <div className="sticky_header">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2>{quiz.name}</h2>
                <div style={{ display: 'flex', flexDirection: 'row', gap: '10px', alignItems: 'center' }}>
                    <CountdownClock endTime={quiz.endTime} />
                    <Button label="Submit" onClick={submitDialog} />
                </div>
            </div>
        </div>
    );
}

function CountdownClock({ endTime }: { endTime: Date }) {
    const [secondsLeft, setSecondsLeft] = useState((endTime.getTime() - Date.now()) / 1000);
    useEffect(() => {
        const interval = setInterval(() => {
            setSecondsLeft((endTime.getTime() - Date.now()) / 1000);
        }, 1000);
        return () => clearInterval(interval);
    }, [endTime]);

    const formatTimer = (s: number) => {
        const days = Math.floor(s / 86400);
        const hours = Math.floor((s % 86400) / 3600);
        const minutes = Math.floor((s % 3600) / 60);
        const seconds = Math.floor(s % 60);
        return `${days > 0 ? `${days}d ` : ''}${hours > 0 ? `${hours}h ` : ''}${minutes}m ${seconds}s`;
    };

    return <Badge size="large" value={`Time Left: ${formatTimer(secondsLeft)}`} severity="secondary" />;
}
