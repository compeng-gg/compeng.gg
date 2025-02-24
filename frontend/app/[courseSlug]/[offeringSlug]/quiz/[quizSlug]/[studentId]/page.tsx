"use client";

import { useEffect, useState, useContext } from "react";
import { useParams } from "next/navigation";
import { fetchApi } from "@/app/lib/api";
import { JwtContext } from "@/app/lib/jwt-provider";
import Navbar from "@/app/components/navbar";
import { QuestionDisplay } from "../../question-display";
import { QuestionData, QuestionState } from "../../question-models";

interface Submission {
    user_id: number;
    username: string;
    started_at: string;
    completed_at: string;
    answers: {
        multiple_choice_answers: { question: string; selected_answer_index: number }[];
        checkbox_answers: { question: string; selected_answer_indices: number[] }[];
        coding_answers: { question: string; solution: string }[];
        written_response_answers: { question: string; response: string }[];
    };
}

export default function StudentSubmissionPage() {
    const { courseSlug, offeringSlug, quizSlug, studentId } = useParams();
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [submission, setSubmission] = useState<Submission | null>(null);
    const [loading, setLoading] = useState(true);
    const [questionData, setQuestionData] = useState<QuestionData[]>([]);
    const [questionStates, setQuestionStates] = useState<QuestionState[]>([]);

    async function fetchSubmission() {
        try {
            const res = await fetchApi(
                jwt,
                setAndStoreJwt,
                `quizzes/admin/${courseSlug}/${quizSlug}/submissions/${studentId}/`,
                "GET"
            );
            if (!res.ok) {
                throw new Error("Failed to fetch submission");
            }
            const data = await res.json();
            setSubmission(data);

            // Convert the submission answers into question display format
            const qData: QuestionData[] = [
                ...data.answers.multiple_choice_answers.map((ans, idx) => ({
                    id: `MC_${idx}`,
                    quizSlug,
                    courseSlug,
                    prompt: ans.question,
                    totalMarks: 1,
                    isMutable: false,
                    questionType: "SELECT",
                    serverQuestionType: "MULTIPLE_CHOICE",
                    options: ["Option 1", "Option 2", "Option 3"], // Placeholder options
                })),
                ...data.answers.checkbox_answers.map((ans, idx) => ({
                    id: `CB_${idx}`,
                    quizSlug,
                    courseSlug,
                    prompt: ans.question,
                    totalMarks: 1,
                    isMutable: false,
                    questionType: "SELECT",
                    serverQuestionType: "MULTIPLE_CHOICE",
                    options: ["Option 1", "Option 2", "Option 3"], // Placeholder options
                })),
                ...data.answers.coding_answers.map((ans, idx) => ({
                    id: `CODE_${idx}`,
                    quizSlug,
                    courseSlug,
                    prompt: ans.question,
                    totalMarks: 10,
                    isMutable: false,
                    questionType: "CODE",
                    serverQuestionType: "CODING",
                    starterCode: ans.solution,
                    programmingLanguage: "PYTHON",
                })),
                ...data.answers.written_response_answers.map((ans, idx) => ({
                    id: `TEXT_${idx}`,
                    quizSlug,
                    courseSlug,
                    prompt: ans.question,
                    totalMarks: 5,
                    isMutable: false,
                    questionType: "TEXT",
                    serverQuestionType: "WRITTEN_RESPONSE",
                })),
            ];
            setQuestionData(qData);

            const qStates: QuestionState[] = qData.map((q, idx) => ({
                value:
                    q.questionType === "SELECT"
                        ? data.answers.multiple_choice_answers[idx]?.selected_answer_index ?? -1
                        : q.questionType === "TEXT"
                        ? data.answers.written_response_answers[idx]?.response ?? ""
                        : q.questionType === "CODE"
                        ? data.answers.coding_answers[idx]?.solution ?? ""
                        : "",
                setValue: () => {}, // Read-only mode for grading
            }));
            setQuestionStates(qStates);
        } catch (error) {
            console.error("Failed to retrieve student submission", error);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchSubmission();
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

                {/* Render each question */}
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                    {questionData.map((q, idx) => (
                        <QuestionDisplay key={q.id} {...q} state={questionStates[idx]} idx={idx} />
                    ))}
                </div>
            </div>
        </>
    );
}
