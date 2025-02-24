"use client";

import { useEffect, useState, useContext } from "react";
import { useParams } from "next/navigation";
import { fetchApi } from "@/app/lib/api";
import { JwtContext } from "@/app/lib/jwt-provider";
import Navbar from "@/app/components/navbar";
import { QuestionDisplay } from "../../question-display";
import { QuestionData, QuestionState, ServerToLocal } from "../../question-models";

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
    const [questions, setQuestions] = useState<QuestionData[]>([]);
    const [loading, setLoading] = useState(true);
    const [questionStates, setQuestionStates] = useState<QuestionState[]>([]);

    async function fetchQuizAndSubmission() {
        try {
            // Fetch the full quiz (to get questions)
            const quizRes = await fetchApi(
                jwt,
                setAndStoreJwt,
                `quizzes/admin/${courseSlug}/${quizSlug}/`,
                "GET"
            );
            if (!quizRes.ok) {
                throw new Error("Failed to fetch quiz details");
            }
            const quizData = await quizRes.json();
            
            const fetchedQuestions: QuestionData[] = quizData.questions.map((q: any) => ({
                id: q.id,
                quizSlug,
                courseSlug,
                prompt: q.prompt,  // ✅ Match answers using this
                totalMarks: q.points,
                isMutable: false, // Read-only for grading
                questionType: ServerToLocal.get(q.question_type) ?? "TEXT",
                serverQuestionType: q.question_type,
                options: q.options ?? [], // For multiple-choice and checkbox
                starterCode: q.starter_code ?? "",
                programmingLanguage: q.programming_language ?? "PYTHON",
            }));
            setQuestions(fetchedQuestions);

            // Fetch the student's submission
            const subRes = await fetchApi(
                jwt,
                setAndStoreJwt,
                `quizzes/admin/${courseSlug}/${quizSlug}/submissions/${studentId}/`,
                "GET"
            );
            if (!subRes.ok) {
                throw new Error("Failed to fetch submission");
            }
            const subData = await subRes.json();
            setSubmission(subData);

            // 🔥 FIXED: Map answers correctly based on prompt (text matching)
            const qStates: QuestionState[] = fetchedQuestions.map((q) => {
                const mcAnswer = subData.answers.multiple_choice_answers.find((a) => a.question === q.prompt);
                const cbAnswer = subData.answers.checkbox_answers.find((a) => a.question === q.prompt);
                const codeAnswer = subData.answers.coding_answers.find((a) => a.question === q.prompt);
                const textAnswer = subData.answers.written_response_answers.find((a) => a.question === q.prompt);

                return {
                    value:
                        q.questionType === "SELECT"
                            ? mcAnswer?.selected_answer_index ?? -1
                            : q.questionType === "CHECKBOX"
                            ? cbAnswer?.selected_answer_indices ?? []
                            : q.questionType === "CODE"
                            ? codeAnswer?.solution ?? ""
                            : q.questionType === "TEXT"
                            ? textAnswer?.response ?? ""
                            : "",
                    setValue: () => {}, // Read-only mode for grading
                };
            });

            setQuestionStates(qStates);
        } catch (error) {
            console.error("Failed to retrieve student submission", error);
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

                {/* Render each question */}
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                    {questions.map((q, idx) => (
                        <QuestionDisplay key={q.id} {...q} state={questionStates[idx]} idx={idx} />
                    ))}
                </div>
            </div>
        </>
    );
}
