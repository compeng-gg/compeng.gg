"use client";

import { Card } from "primereact/card";
import CodeEditor from "../../components/code-editor";
import TextEditor from "../../components/text-editor";
import SelectEditor from "../../components/select-editor";
import { useState } from "react";

interface GradingQuestionDisplayProps {
    question: {
        prompt: string;
        points: number;
        options?: string[];
        programming_language?: string;
    };
    studentAnswer: any; // The student's submitted answer
}

export default function GradingQuestionDisplay({ question, studentAnswer }: GradingQuestionDisplayProps) {
    const [comment, setComment] = useState("");
    const [grade, setGrade] = useState<number | "">(0);

    return (
        <Card
            title={question.prompt}
            style={{
                marginBottom: "20px",
                background: "#fff",
                borderRadius: "8px",
                padding: "15px",
                boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
            }}
        >
            {/* Student Answer Section */}
            <div style={{ marginBottom: "15px" }}>
                <strong>Student Answer:</strong>

                {/* ✅ Multiple-Choice & Checkbox Questions (Using SelectEditor) */}
                {question.options ? (
                    <SelectEditor
                        props={{
                            state: {
                                value: studentAnswer?.selected_answer_index ?? -1,
                                setValue: () => {}, // Read-only
                            },
                            options: question.options,
                        }}
                        save={() => {}} // ✅ Required prop
                    />
                ) : question.programming_language ? (
                    // ✅ Coding Questions (Show only student's code)
                    <CodeEditor
                        props={{
                            id: "code-question",
                            quizSlug: "",
                            courseSlug: "",
                            prompt: question.prompt,
                            totalMarks: question.points,
                            starterCode: "",
                            isMutable: false, // Read-only
                            questionType: "CODE",
                            serverQuestionType: "CODING",
                            programmingLanguage: (question.programming_language as "PYTHON" | "C_PP" | "C") ?? "PYTHON",
                            state: {
                                value: studentAnswer?.solution ?? "No answer provided",
                                setValue: () => {},
                            },
                        }}
                        save={() => {}} // ✅ Required prop
                    />
                ) : (
                    // ✅ Written Response Questions
                    <TextEditor
                        state={{
                            value: studentAnswer?.response ?? "No answer provided",
                            setValue: () => {},
                        }}
                        save={() => {}} // ✅ Required prop
                    />
                )}
            </div>

            {/* 🔥 Grading Section - Styled to Look Clean */}
            <div style={{ display: "flex", gap: "15px", alignItems: "center", marginTop: "15px" }}>
                {/* Comment Box */}
                <div style={{ flex: "2" }}>
                    <label><strong>Comments:</strong></label>
                    <textarea
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="Leave feedback for the student..."
                        style={{
                            width: "100%",
                            minHeight: "50px",
                            padding: "8px",
                            borderRadius: "5px",
                            border: "1px solid #ccc",
                        }}
                    />
                </div>

                {/* Grade Box */}
                <div style={{ flex: "1", textAlign: "right" }}>
                    <label><strong>Grade:</strong></label>
                    <input
                        type="number"
                        value={grade}
                        onChange={(e) => setGrade(e.target.value ? Number(e.target.value) : "")}
                        min="0"
                        max={question.points}
                        style={{
                            width: "60px",
                            textAlign: "center",
                            padding: "5px",
                            borderRadius: "5px",
                            border: "1px solid #ccc",
                        }}
                    />
                    / {question.points}
                </div>
            </div>
        </Card>
    );
}
