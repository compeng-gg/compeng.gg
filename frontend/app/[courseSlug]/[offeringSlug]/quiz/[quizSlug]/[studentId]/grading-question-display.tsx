"use client";

import { Card } from "primereact/card";
import { Badge } from "primereact/badge";
import CodeEditor from "../../components/code-editor";
import TextEditor from "../../components/text-editor";
import SelectEditor from "../../components/select-editor";
import { useState } from "react";

interface GradingQuestionDisplayProps {
    idx?: number;
    question: {
        prompt: string;
        points: number;
        options?: string[];
        programming_language?: string;
    };
    studentAnswer: any; // The student's submitted answer
}

export default function GradingQuestionDisplay({ idx = 1, question, studentAnswer }: GradingQuestionDisplayProps) {
    const [comment, setComment] = useState("");
    const [grade, setGrade] = useState<number | "">(0);

    return (
        <Card
            title={`Question ${idx}`} // ✅ Question Number Added
            subTitle={question.prompt}
            style={{
                marginBottom: "20px",
                background: "#fff",
                borderRadius: "8px",
                padding: "15px",
                boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
                position: "relative",
            }}
            header={<GradeBadge totalAvailable={question.points} />} // ✅ Points Badge at Top-Right
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
                            id: `code-question-${idx}`,
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

            {/* 🔥 Grading Section - Now Smaller and in Bottom-Right */}
            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "15px" }}>
                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                        border: "1px solid #ccc",
                        padding: "6px 10px",
                        borderRadius: "6px",
                        background: "#f9f9f9",
                    }}
                >
                    <strong style={{ marginRight: "8px" }}>Grade:</strong>
                    <TextEditor
                        state={{
                            value: grade.toString(),
                            setValue: (newValue) => setGrade(newValue ? Number(newValue) : ""),
                        }}
                        save={() => {}} // ✅ Required prop
                        style={{
                            width: "50px",
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
