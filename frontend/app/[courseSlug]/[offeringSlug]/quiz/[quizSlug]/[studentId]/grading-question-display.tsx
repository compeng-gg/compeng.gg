'use client';

import { useState, useEffect, useContext } from 'react';
import { Card } from 'primereact/card';
import { Badge } from 'primereact/badge';
import CodeEditor from '../../components/code-editor';
import TextEditor from '../../components/text-editor';
import SelectEditor from '../../components/select-editor';
import CheckboxEditor from '../../components/checkbox-editor-VA';
import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';
import { useParams } from 'next/navigation';

interface GradingQuestionDisplayProps {
    idx?: number;
    question: {
        id: string;  
        prompt: string;
        points: number;
        options?: string[];
        programming_language?: string;
        correct_option_index?: number;
        correct_option_indices?: number[];
        question_type: string;  
    };
    studentAnswer: any;
    executions?: {
        solution: string;
        result: any;
        stderr: string;
        status: string;
    }[];
    grade?: number | null;
    comment?: string | null;
}

export default function GradingQuestionDisplay({ 
    idx = 1, 
    question, 
    studentAnswer, 
    executions, 
    grade: initialGrade, 
    comment: initialComment 
}: GradingQuestionDisplayProps) {
    
    const { courseSlug, quizSlug, studentId } = useParams();
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    
    const [comment, setComment] = useState(initialComment ?? studentAnswer?.comment ?? '');
    const [grade, setGrade] = useState<number | null>(() => {
        if (initialGrade !== null && initialGrade !== undefined) {
            return initialGrade; 
        }
    
        let autoGradedScore: number | null = null;
    
        if (question.correct_option_index !== undefined) {
            autoGradedScore = studentAnswer?.selected_answer_index === question.correct_option_index ? question.points : 0;
        } 
        else if (question.correct_option_indices !== undefined) {
            const studentSelection = new Set(studentAnswer?.selected_answer_indices || []);
            const correctSelection = new Set(question.correct_option_indices);
    
            const correctCount = [...studentSelection].filter((idx) => correctSelection.has(idx)).length;
            const incorrectCount = [...studentSelection].filter((idx) => !correctSelection.has(idx)).length;
            const totalCorrect = correctSelection.size;
            autoGradedScore = Math.round(Math.max(0, (correctCount / totalCorrect) * question.points - incorrectCount));
        } 
        else if (question.programming_language) {
            if (executions && executions.length > 0) {
                const highestGrade = Math.max(...executions.map(exec => exec.result?.grade ?? 0));
                autoGradedScore = Math.round(highestGrade * question.points);
            } else {
                autoGradedScore = 0;
            }
        }
    
        if (autoGradedScore !== null) {
            // ✅ Use `autoGradedScore` instead of `grade`
            updateGradeOrComment(question.id, autoGradedScore, comment ?? '');
        }
    
        return autoGradedScore ?? null;
    });
    
    
    

    /** ✅ **Function to update grade & comment in backend** */
    async function updateGradeOrComment(questionId: string, grade: number | null, comment: string) {
        await fetchApi(jwt, setAndStoreJwt, 
            `quizzes/admin/${courseSlug}/${quizSlug}/submissions/${studentId}/update-question/`, 
            'POST', {
                question_id: questionId, // ✅ Use question_id instead of prompt
                grade: grade,
                comment: comment
            }
        );
    }

    /** ✅ **Trigger backend update on grade/comment change** */
    useEffect(() => {
        const timeout = setTimeout(() => {
            updateGradeOrComment(question.id, grade ?? null, comment ?? '');
        }, 500); 

        return () => clearTimeout(timeout);
    }, [grade, comment]);

    return (
        <Card
            title={`Question ${idx}`}
            subTitle={question.prompt}
            style={{
                marginBottom: '20px',
                background: '#fff',
                borderRadius: '8px',
                padding: '15px',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                position: 'relative',
            }}
            header={<GradeBadge totalAvailable={question.points} />}
        >
            <div style={{ marginBottom: '15px' }}>
                <strong>Student Answer:</strong>

                {question.options ? (
                    question.correct_option_indices ? (
                        <CheckboxEditor
                            props={{
                                state: {
                                    value: studentAnswer?.selected_answer_indices || [],
                                    setValue: () => {}, 
                                },
                                options: question.options,
                            }}
                            save={() => {}}
                        />
                    ) : (
                        <SelectEditor
                            props={{
                                state: {
                                    value: studentAnswer?.selected_answer_index ?? -1,
                                    setValue: () => {}, 
                                },
                                options: question.options,
                            }}
                            save={() => {}}
                        />
                    )
                ) : question.programming_language ? (
                    <CodeEditor
                        props={{
                            id: `code-question-${idx}`,
                            quizSlug: '',
                            courseSlug: '',
                            prompt: question.prompt,
                            totalMarks: question.points,
                            isMutable: false,
                            questionType: 'CODE',
                            serverQuestionType: 'CODING',
                            programmingLanguage: question.programming_language ?? 'PYTHON',
                            state: {
                                value: studentAnswer?.solution ?? 'No answer provided',
                                setValue: () => {},
                            },
                            executions: executions,
                        }}
                        save={() => {}}
                    />
                ) : (
                    <TextEditor
                        state={{
                            value: studentAnswer?.response ?? 'No answer provided',
                            setValue: () => {},
                        }}
                        save={() => {}}
                    />
                )}
            </div>

            {/* 🔥 Grading Section */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '15px' }}>
                <div style={{ flex: '2', marginRight: '20px' }}>
                    <label><strong>Comments:</strong></label>
                    <TextEditor
                        state={{
                            value: comment,
                            setValue: (newValue) => setComment(newValue),
                        }}
                        save={() => {}}
                    />
                </div>

                <div
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        border: '1px solid #ccc',
                        padding: '5px 8px',
                        borderRadius: '6px',
                        background: '#f9f9f9',
                        minWidth: '100px',
                        height: '36px',
                    }}
                >
                    <strong style={{ marginRight: '8px' }}>Grade:</strong>
                    <input
                        type="text"
                        value={grade !== null ? grade : ''}
                        onChange={(e) => {
                            const value = e.target.value.replace(/\D/, '');
                            setGrade(value ? parseInt(value) : null);
                        }}
                        pattern="[0-9]*"
                        inputMode="numeric"
                        style={{
                            width: '50px',
                            padding: '3px 5px',
                            border: '1px solid #ccc',
                            borderRadius: '4px',
                            textAlign: 'center',
                        }}
                    />
                </div>
            </div>
        </Card>
    );
}

/** ✅ **Grade Badge at Top-Right of Each Card** */
function GradeBadge({ totalAvailable }: { totalAvailable: number }) {
    return (
        <Badge
            size="large"
            value={`Points: ${totalAvailable}`}
            severity="info"
            style={{
                fontSize: '14px',
                padding: '6px 10px',
                position: 'absolute',
                top: '10px',
                right: '10px',
            }}
        />
    );
}
