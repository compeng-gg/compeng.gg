"use client";

import { Card } from "primereact/card";
import { Badge } from "primereact/badge";
import CodeEditor from "../../components/code-editor";
import TextEditor from "../../components/text-editor";
import SelectEditor from "../../components/select-editor";
import CheckboxEditor from "../../components/checkbox-editor-VA";
import { useState } from "react";

interface GradingQuestionDisplayProps {
    idx?: number;
    question: {
        prompt: string;
        points: number;
        options?: string[];
        programming_language?: string;
        correct_option_index?: number;
        correct_option_indices?: number[];
    };
    studentAnswer: any;
    executions?: { 
        solution: string;
        result: any;
        stderr: string;
        status: string;
    }[];
    grade?: number | null;
    comment?: string | null; // ✅ Pass comment as a prop
}



export default function GradingQuestionDisplay({ idx = 1, question, studentAnswer, executions, grade: initialGrade }: GradingQuestionDisplayProps) {    
    const [comment, setComment] = useState(() => studentAnswer?.comment ?? "");

    const [grade, setGrade] = useState(() => {
        if (initialGrade !== null) {
            return initialGrade; // ✅ Use existing grade if set
        }

        if (question.correct_option_index !== undefined) {
            // ✅ Auto-grade multiple choice: Full points if correct, 0 otherwise
            return studentAnswer?.selected_answer_index === question.correct_option_index ? question.points : 0;
        } else if (question.correct_option_indices !== undefined) {
            // ✅ Auto-grade checkbox (Partial Credit)
            const studentSelection = new Set(studentAnswer?.selected_answer_indices || []);
            const correctSelection = new Set(question.correct_option_indices);

            const correctCount = [...studentSelection].filter((idx) => correctSelection.has(idx)).length;
            const incorrectCount = [...studentSelection].filter((idx) => !correctSelection.has(idx)).length;

            const totalCorrect = correctSelection.size;
            const partialScore = Math.max(0, (correctCount / totalCorrect) * question.points - incorrectCount);
            
            return Math.round(partialScore);
        } else if (question.programming_language) {
            // ✅ Auto-grade coding question based on execution results
            if (executions && executions.length > 0) {
                const highestGrade = Math.max(...executions.map(exec => exec.result?.grade ?? 0));
                return Math.round(highestGrade * question.points);
            }
            return 0; // Default to zero if no executions exist
        }
        return null;
    });

    return (
        <Card
            title={`Question ${idx}`}
            subTitle={question.prompt}
            style={{
                marginBottom: "20px",
                background: "#fff",
                borderRadius: "8px",
                padding: "15px",
                boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
                position: "relative",
            }}
            header={<GradeBadge totalAvailable={question.points} />}
        >
            <div style={{ marginBottom: "15px" }}>
                <strong>Student Answer:</strong>

                {/* ✅ Multiple-Choice & Checkbox Questions */}
                {question.options ? (
                    question.correct_option_indices ? (
                        <CheckboxEditor
                            props={{
                                state: {
                                    value: studentAnswer?.selected_answer_indices || [],
                                    setValue: () => {}, // Read-only
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
                                    setValue: () => {}, // Read-only
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
                            quizSlug: "",
                            courseSlug: "",
                            prompt: question.prompt,
                            totalMarks: question.points,
                            isMutable: false,
                            questionType: "CODE",
                            serverQuestionType: "CODING",
                            programmingLanguage: question.programming_language ?? "PYTHON",
                            state: {
                                value: studentAnswer?.solution ?? "No answer provided",
                                setValue: () => {},
                            },
                            executions: executions, // ✅ Pass executions explicitly
                        }}
                        save={() => {}}
                    />
                ) : (
                    <TextEditor
                        state={{
                            value: studentAnswer?.response ?? "No answer provided",
                            setValue: () => {},
                        }}
                        save={() => {}}
                    />
                )}
            </div>

            {/* 🔥 Grading Section */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "15px" }}>
                <div style={{ flex: "2", marginRight: "20px" }}>
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
                        display: "flex",
                        alignItems: "center",
                        border: "1px solid #ccc",
                        padding: "5px 8px",
                        borderRadius: "6px",
                        background: "#f9f9f9",
                        minWidth: "100px",
                        height: "36px",
                    }}
                >
                    <strong style={{ marginRight: "8px" }}>Grade:</strong>
                    <input
                        type="text"
                        value={grade !== null ? grade : ""}
                        onChange={(e) => {
                            const value = e.target.value.replace(/\D/, ""); 
                            setGrade(value ? parseInt(value) : null);
                        }}
                        pattern="[0-9]*"
                        inputMode="numeric"
                        style={{
                            width: "50px",
                            padding: "3px 5px",
                            border: "1px solid #ccc",
                            borderRadius: "4px",
                            textAlign: "center",
                        }}
                    />
                </div>
            </div>
        </Card>
    );
}

/* 🔹 Helper Component for Displaying Grade Badge (Top-Right of Each Card) */
function GradeBadge({ totalAvailable }: { totalAvailable: number }) {
    return (
        <Badge
            size="large"
            value={`Points: ${totalAvailable}`}
            severity="info"
            style={{
                fontSize: "14px",
                padding: "6px 10px",
                position: "absolute",
                top: "10px",
                right: "10px",
            }}
        />
    );
}