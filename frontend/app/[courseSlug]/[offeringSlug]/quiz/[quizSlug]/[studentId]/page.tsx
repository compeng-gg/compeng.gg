"use client";

import { useEffect, useState, useContext } from "react";
import { useParams } from "next/navigation";
import { fetchApi } from "@/app/lib/api";
import { JwtContext } from "@/app/lib/jwt-provider";
import Navbar from "@/app/components/navbar";
import GradingQuestionDisplay from "./grading-question-display";

interface Question {
    prompt: string;
    points: number;
    order: number;
    options?: string[];
    correct_option_index?: number;
    correct_option_indices?: number[];
    starter_code?: string;
    programming_language?: string;
    executions?: {  // ✅ New field to store execution results
        solution: string;
        result: any;
        stderr: string;
        status: string;
    }[];
}


interface Submission {
    user_id: number;
    username: string;
    started_at: string;
    completed_at: string;
    answers: {
        multiple_choice_answers: { question: string; selected_answer_index: number; grade: number | null; comment: string | null }[];
        checkbox_answers: { question: string; selected_answer_indices: number[]; grade: number | null; comment: string | null }[];
        coding_answers: { question: string; solution: string; executions?: any[]; grade: number | null; comment: string | null }[];
        written_response_answers: { question: string; response: string; grade: number | null; comment: string | null }[];
    };
}



export default function StudentSubmissionPage() {
    const { courseSlug, offeringSlug, quizSlug, studentId } = useParams();
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [questions, setQuestions] = useState<Question[]>([]);
    const [submission, setSubmission] = useState<Submission | null>(null);
    const [loading, setLoading] = useState(true);
    const [gradeSubmitted, setGradeSubmitted] = useState(false);


    async function fetchQuizAndSubmission() {
        try {
            const quizRes = await fetchApi(
                jwt,
                setAndStoreJwt,
                `quizzes/admin/${courseSlug}/${quizSlug}/`,
                "GET"
            );
            if (!quizRes.ok) throw new Error("Failed to fetch quiz details");
            const quizData = await quizRes.json();
            setQuestions(quizData.questions);

            const subRes = await fetchApi(
                jwt,
                setAndStoreJwt,
                `quizzes/admin/${courseSlug}/${quizSlug}/submissions/${studentId}/`,
                "GET"
            );
            if (!subRes.ok) throw new Error("Failed to fetch submission");

            const submissionData = await subRes.json();
            setSubmission(submissionData);
        } catch (error) {
            console.error("Failed to retrieve data", error);
        } finally {
            setLoading(false);
        }
    }
    

    useEffect(() => {
        fetchQuizAndSubmission();
    }, [courseSlug, quizSlug, studentId, jwt, setAndStoreJwt]);

    if (loading) {
        return (
            <>
                <Navbar />
                <p>Loading student submission...</p>
            </>
        );
    }

    return (
        <>
            <Navbar />
            <div style={{ padding: "20px" }}>
                <h2>{submission?.username}'s Submission</h2>
                <p>Started at: {new Date(submission?.started_at ?? "").toLocaleString()}</p>
                <p>Completed at: {new Date(submission?.completed_at ?? "").toLocaleString()}</p>

                {/* Render questions with answers */}
                <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                    {questions.map((question, idx) => {
                        const matchingAnswer =
                            submission?.answers.multiple_choice_answers.find((a) => a.question === question.prompt) ||
                            submission?.answers.checkbox_answers.find((a) => a.question === question.prompt) ||
                            submission?.answers.coding_answers.find((a) => a.question === question.prompt) ||
                            submission?.answers.written_response_answers.find((a) => a.question === question.prompt);

                            const executions = submission?.answers.coding_answers.find((a) => a.question === question.prompt)?.executions || [];

                        return (
                            <GradingQuestionDisplay
                                key={idx}
                                idx={idx + 1}
                                question={{
                                    ...question,
                                    correct_option_index: question.correct_option_index,
                                    correct_option_indices: question.correct_option_indices,
                                }}
                                studentAnswer={matchingAnswer}
                                executions={executions}
                                grade={matchingAnswer?.grade}
                                comment={matchingAnswer?.comment}
                            />
                        );
                    })}
                </div>
            </div>
            <button
                onClick={() => {
                    setGradeSubmitted(true);
                    setTimeout(() => setGradeSubmitted(false), 3000); // Auto-hide after 3 seconds
                }}
                style={{
                    position: "fixed",
                    bottom: "20px",
                    right: "20px",
                    backgroundColor: "#007bff",
                    color: "#fff",
                    padding: "10px 20px",
                    borderRadius: "5px",
                    border: "none",
                    cursor: "pointer",
                    fontSize: "16px",
                    boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
                }}
            >
                Submit Grade
            </button>
            {gradeSubmitted && (
                <div
                    style={{
                        position: "fixed",
                        bottom: "70px",
                        right: "100px",
                        backgroundColor: "#28a745",
                        color: "#fff",
                        padding: "10px 15px",
                        borderRadius: "5px",
                        fontSize: "14px",
                        display: "flex",
                        alignItems: "center",
                        gap: "10px",
                        boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
                    }}
                >
                    Grade successfully submitted!
                    <button
                        onClick={() => setGradeSubmitted(false)}
                        style={{
                            background: "none",
                            border: "none",
                            color: "#fff",
                            fontSize: "14px",
                            cursor: "pointer",
                        }}
                    >
                        ✖
                    </button>
                </div>
            )}

        </>
    );
}
