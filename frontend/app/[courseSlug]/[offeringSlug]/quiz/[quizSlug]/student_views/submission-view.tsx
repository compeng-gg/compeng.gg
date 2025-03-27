'use client';

import { useEffect, useState, useContext } from 'react';
import { useParams } from 'next/navigation';
import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';
import { Badge } from 'primereact/badge';
import { Card } from 'primereact/card';
import CodeEditor from '../../components/code-editor';
import TextEditor from '../../components/text-editor';
import SelectEditor from '../../components/select-editor';
import CheckboxEditor from '../../components/checkbox-editor-VA';

interface Question {
    id: string;
    prompt: string;
    points: number;
    options?: string[];
    correct_option_index?: number;
    correct_option_indices?: number[];
    starter_code?: string;
    programming_language?: string;
    question_type: string;
}

interface Submission {
    started_at: string;
    completed_at: string;
    answers: {
        multiple_choice_answers: any[];
        checkbox_answers: any[];
        coding_answers: any[];
        written_response_answers: any[];
    };
}

export default function ViewOnlyQuizSubmission() {
    const { courseSlug, quizSlug } = useParams();
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [questions, setQuestions] = useState<Question[]>([]);
    const [submission, setSubmission] = useState<Submission | null>(null);
    const [loading, setLoading] = useState(true);

    async function fetchData() {
        try {
            const quizRes = await fetchApi(jwt, setAndStoreJwt, `quizzes/admin/${courseSlug}/${quizSlug}/`, 'GET');
            const quizData = await quizRes.json();
            setQuestions(quizData.questions || []);

            const subRes = await fetchApi(jwt, setAndStoreJwt, `quizzes/${courseSlug}/${quizSlug}/submission/`, 'GET');
            const subData = await subRes.json();
            setSubmission(subData);
        } catch (err) {
            console.error('Failed to load submission view', err);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchData();
    }, [courseSlug, quizSlug]);

    if (loading) {
        return <p>Loading submission...</p>;
    }

    return (
        <div style={{ padding: '20px' }}>
            <h2>Quiz Submission Results</h2>
            <p>Started: {new Date(submission?.started_at ?? '').toLocaleString()}</p>
            <p>Completed: {new Date(submission?.completed_at ?? '').toLocaleString()}</p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {questions.map((question, idx) => {
                    const matchingAnswer =
                        submission?.answers.multiple_choice_answers.find((a) => a.question_id === question.id) ||
                        submission?.answers.checkbox_answers.find((a) => a.question_id === question.id) ||
                        submission?.answers.coding_answers.find((a) => a.question_id === question.id) ||
                        submission?.answers.written_response_answers.find((a) => a.question_id === question.id);

                    const executions = submission?.answers.coding_answers.find((a) => a.question_id === question.id)?.executions || [];

                    return (
                        <Card
                            key={idx}
                            title={`Question ${idx + 1}`}
                            subTitle={question.prompt}
                            style={{ background: '#fff', borderRadius: '8px', padding: '15px' }}
                        >
                            <strong>Student Answer:</strong>
                            <div style={{ marginTop: '10px' }}>
                                {question.question_type === 'CHECKBOX' ? (
                                    <CheckboxEditor
                                        props={{
                                            state: {
                                                value: matchingAnswer?.selected_answer_indices || [],
                                                setValue: () => {},
                                            },
                                            options: question.options || [],
                                        }}
                                        save={() => {}}
                                    />
                                ) : question.question_type === 'MULTIPLE_CHOICE' ? (
                                    <SelectEditor
                                        props={{
                                            state: {
                                                value: matchingAnswer?.selected_answer_index ?? -1,
                                                setValue: () => {},
                                            },
                                            options: question.options || [],
                                        }}
                                        save={() => {}}
                                    />
                                ) : question.question_type === 'CODING' ? (
                                    <CodeEditor
                                        props={{
                                            id: `code-question-${idx}`,
                                            quizSlug: quizSlug as string,
                                            courseSlug: courseSlug as string,
                                            prompt: question.prompt,
                                            totalMarks: question.points,
                                            isMutable: false,
                                            questionType: 'CODE',
                                            serverQuestionType: 'CODING',
                                            programmingLanguage: question.programming_language ?? 'PYTHON',
                                            state: {
                                                value: matchingAnswer?.solution ?? 'No answer provided',
                                                setValue: () => {},
                                            },
                                            executions: executions,
                                        }}
                                        save={() => {}}
                                    />
                                ) : (
                                    <TextEditor
                                        state={{
                                            value: matchingAnswer?.response ?? 'No answer provided',
                                            setValue: () => {},
                                        }}
                                        save={() => {}}
                                    />
                                )}
                            </div>
                        </Card>
                    );
                })}
            </div>
        </div>
    );
}
