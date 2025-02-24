"use client";

import { useState } from "react";

interface GradingQuestionDisplayProps {
    question: {
        prompt: string;
        points: number;
        options?: string[];
        starter_code?: string;
        programming_language?: string;
    };
    studentAnswer: any; // The student's submitted answer
}

export default function GradingQuestionDisplay({ question, studentAnswer }: GradingQuestionDisplayProps) {
    const [comment, setComment] = useState("");
    const [grade, setGrade] = useState<number | "">(0);

    return (
        <div style={{
            border: "1px solid #ddd",
            borderRadius: "8px",
            padding: "15px",
            background: "#f9f9f9"
        }}>
            <h3>{question.prompt}</h3>
            
            {/* Student Answer */}
            <div style={{ marginBottom: "10px", fontStyle: "italic" }}>
                <strong>Student Answer:</strong> {studentAnswer?.solution || studentAnswer?.response || "No answer provided"}
            </div>

            {/* Instructor Grading Section */}
            <div style={{ display: "flex", gap: "15px", alignItems: "center" }}>
                {/* Comment Box */}
                <div style={{ flex: "2" }}>
                    <label>Comments:</label>
                    <textarea
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="Leave feedback for the student..."
                        style={{ width: "100%", minHeight: "50px", padding: "5px" }}
                    />
                </div>

                {/* Grade Box */}
                <div style={{ flex: "1", textAlign: "right" }}>
                    <label>Grade:</label>
                    <input
                        type="number"
                        value={grade}
                        onChange={(e) => setGrade(e.target.value ? Number(e.target.value) : "")}
                        min="0"
                        max={question.points}
                        style={{ width: "50px", textAlign: "center" }}
                    /> 
                    / {question.points}
                </div>
            </div>
        </div>
    );
}
