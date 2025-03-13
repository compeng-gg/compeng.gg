'use client';

import Navbar from '@/app/components/navbar';
import LoginRequired from '@/app/lib/login-required';
import { useContext, useEffect, useState } from 'react';
import QuizDisplay, { QuizProps } from '../quiz-display';
import { BaseQuestionData, CodeQuestionData, QuestionData, QuestionProps, QuestionViewMode, QuestionState, QuestionType, SelectQuestionData, ServerToLocal, TextQuestionData } from '../question-models';
import { Card } from 'primereact/card';
import { QuestionDisplay } from '../question-display';
import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';
import { getQuestionDataFromRaw } from '../quiz-utilities';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Badge } from 'primereact/badge';
import { time } from 'console';
import { confirmDialog, ConfirmDialog } from 'primereact/confirmdialog';
import { Button } from 'primereact/button';

const now = new Date();
const oneHourBefore = new Date(now.getTime() - 1 * 60 * 60 * 1000);
const twoHoursLater = new Date(now.getTime() + 2 * 60 * 60 * 1000); // Add 2 hours in milliseconds


export default function Page({ params }: { params: { courseSlug: string, quizSlug: string } }) {
    const { courseSlug, quizSlug } = params;
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [quiz, setQuiz] = useState<QuizProps | undefined>(undefined);

    const [loaded, setLoaded] = useState<boolean>(false);
    const [questionData, setQuestionData] = useState<QuestionData[]>([]);
    const [questionStates, setQuestionStates] = useState<QuestionState[]>([]);

    async function fetchQuiz() {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `${courseSlug}/quiz/${quizSlug}`, 'GET');
            const data = await res.json();
            const retQuiz: QuizProps = {
                startTime: new Date(data.start_unix_timestamp * 1000),
                endTime: new Date(data.end_unix_timestamp * 1000),
                quizSlug: quizSlug,
                name: data.title,
                courseSlug: courseSlug
            };
            console.log('Quiz' + JSON.stringify(data, null, 2));
            setQuiz(retQuiz);
            const qData = data.questions.map((rawData, idx) => getQuestionDataFromRaw(rawData,quizSlug, courseSlug, data.images[idx]));
            setQuestionData(qData);
            const questionStates = qData.map((questionData, idx) => ({
                value: getStartingStateValue(questionData, data.questions[idx]),
                setValue: (newValue) => {
                    setQuestionStates((questionStates) => 
                        questionStates.map((state, currIdx) => currIdx == idx ? {...state, value: newValue} : state)
                    );
                }
            }));
            setQuestionStates(questionStates);

        } catch (error) {
            console.error('Failed to retrieve quiz', error);
        }
    }

    async function submitQuiz() {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `${courseSlug}/quiz/${quizSlug}/complete/`, 'POST', {});
            if (!res.ok) {
                throw new Error('Failed to submit quiz');
            }
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
    }, [loaded]);
    //If quiz not found
    if(!loaded){
        return (
            <LoginRequired>
                <Navbar />

                <h3 style={{ color: 'yellow' }}>{`Loading quiz ${quizSlug}...`}</h3>
            </LoginRequired>
        );
    }

    if (!quiz) {
        return (
            <LoginRequired>
                <Navbar />

                <h3 style={{ color: 'yellow' }}>{`quiz ${quizSlug} not found for course ${courseSlug}`}</h3>
            </LoginRequired>
        );
    }

    //If quiz in future
    if (quiz.startTime > now) {
        return (
            <LoginRequired>
                <Navbar />
                <QuizDisplay {...quiz} />
            </LoginRequired>
        );
    }

    const acceptSubmit = () => {
        submitQuiz();
    };

    const submitDialog = () => {
        confirmDialog({
            message: 'Are you sure you want to submit your answers?',
            header: 'Confirmation',
            icon: 'pi pi-exclamation-triangle',
            defaultFocus: 'accept',
            accept: acceptSubmit,
            reject: () => {}
        });
    };

    return (
        <LoginRequired>
            <Navbar />
            <QuizWritingHeader quiz={quiz} submitDialog={submitDialog} />
            <ConfirmDialog />
            <div style={{ display: 'flex', gap: '10px', width: '100%', flexDirection: 'column' }}>
                {questionStates.map((state, idx) => (
                    <QuestionDisplay
                        key={questionData[idx].id || idx} // use unique id if available, otherwise fallback to index
                        {...questionData[idx]}
                        state={state}
                        idx={idx}
                    />
                ))}
            </div>
        </LoginRequired>
    );
}

function getStartingStateValue(questionData: QuestionData, rawData: any): any {
    switch (questionData.questionType) {
    case 'CODE':
        return (rawData.solution) ?? ((questionData as CodeQuestionData).starterCode || '');
    case 'SELECT':
        return (rawData.selected_answer_index) ?? -1; // Default to no option selected
    case 'TEXT':
        return (rawData.response) ?? '';
    case 'MULTI_SELECT':
        return (rawData.selected_answer_indices) ?? [];
    default:
        throw new Error(`Unsupported question type: ${JSON.stringify(questionData)}`);
    }
}

function QuizWritingHeader({ quiz, submitDialog }: { quiz: QuizProps, submitDialog: () => void }) {
    return (
        <div className="sticky_header">
            <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h2>{`${quiz.name}`}</h2>
                </div>
                <div style={{ display: 'flex', flexDirection: 'row', gap: '10px', alignItems: 'center' }}>
                    <CountdownClock endTime={quiz.endTime} />
                    <Button label="Submit" onClick={submitDialog}/> 
                </div>
            </div>
        </div>
    );
}

function CountdownClock({ endTime }: { endTime: Date }) {
    const [secondsLeft, setSecondsLeft] = useState<number>((endTime.getTime() - new Date().getTime()) / 1000);
    useEffect(() => {
        const interval = setInterval(() => {
            setSecondsLeft((endTime.getTime() - new Date().getTime()) / 1000);
        }, 1000);
        return () => clearInterval(interval);
    }, [endTime]);

    const formatTimer = (secondsLeft: number) => {
        let timeString = '';
        const totalHours = Math.floor(secondsLeft / 3600);
        const days = Math.floor(totalHours / 24);
        if(days > 0){
            timeString = `${days}d `;
        }
        const hours = totalHours % 24;
        if(hours > 0){
            timeString = timeString + ` ${hours}h `;
        }
        const minutes = Math.floor(secondsLeft / 60) % 60;
        const seconds = Math.floor(secondsLeft) % 60;
        if(timeString == ''){
            return `${minutes}:${seconds}`;
        } else {
            return timeString + ` ${minutes}m`;
        }

    };

    return (
        <div>
            <Badge size="large" value={`Time Left: ${formatTimer(secondsLeft)}`} severity="secondary" />
        </div>
    );
}

export function useInitializeQuestionStates(questionDataList: QuestionData[]) {
  return questionDataList.map((questionData) => {
    const [value, setValue] = useState(() => getDefaultStateValue(questionData));

    return {
      value,
      setValue,
    };
  });
}
