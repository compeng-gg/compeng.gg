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
    const [grade, setGrade] = useState("");

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

            {/* 🔥 Grading Section - Now Smaller and Properly Positioned */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "15px" }}>
                {/* 🔹 Comment Box (TextEditor) */}
                <div style={{ flex: "2", marginRight: "20px" }}>
                    <label><strong>Comments:</strong></label>
                    <TextEditor
                        state={{
                            value: comment,
                            setValue: (newValue) => setComment(newValue),
                        }}
                        save={() => {}} // ✅ Required prop
                    />
                </div>

                {/* 🔹 Grade Box (Now Uses Smaller `input` Instead of `TextEditor`) */}
                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                        border: "1px solid #ccc",
                        padding: "5px 8px",
                        borderRadius: "6px",
                        background: "#f9f9f9",
                        minWidth: "100px",
                        height: "36px", // ✅ Smaller height
                    }}
                >
                    <strong style={{ marginRight: "8px" }}>Grade:</strong>
                    <input
                        type="text" // ✅ Switch to text to remove number spinner
                        value={grade}
                        onChange={(e) => {
                            const value = e.target.value.replace(/\D/, ""); // ✅ Allow only digits
                            setGrade(value);
                        }}
                        pattern="[0-9]*" // ✅ Mobile-friendly numeric input
                        inputMode="numeric" // ✅ Optimized for mobile keyboards
                        style={{
                            width: "50px", // ✅ Small width for 3-digit input
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
