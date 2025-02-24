"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { fetchApi } from "@/app/lib/api";
import { Button } from "primereact/button";
import Link from "next/link";

interface Submission {
    user_id: number;
    username: string;
    started_at: string;
    completed_at: string;
}

export default function QuizSubmissionsPage() {
    const { courseSlug, offeringSlug, quizSlug } = useParams();
    const [submissions, setSubmissions] = useState<Submission[]>([]);
    const [loading, setLoading] = useState(true);

    async function fetchSubmissions() {
        try {
            const res = await fetchApi(
                null, // No JWT needed for now
                null,
                `quizzes/admin/${courseSlug}/${quizSlug}/submissions/`,
                "GET"
            );
            const data = await res.json();
            setSubmissions(data);
        } catch (error) {
            console.error("Failed to retrieve submissions", error);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchSubmissions();
    }, [courseSlug, quizSlug]);

    if (loading) {
        return <p>Loading submissions...</p>;
    }

    if (submissions.length === 0) {
        return <p>No submissions found.</p>;
    }

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "10px", width: "100%" }}>
            <h2>Quiz Submissions</h2>
            {submissions.map((submission) => (
                <div key={submission.user_id} style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    padding: "10px",
                    border: "1px solid #ccc",
                    borderRadius: "8px",
                    background: "#f9f9f9",
                }}>
                    <div>
                        <p><strong>{submission.username}</strong></p>
                        <p>Started: {new Date(submission.started_at).toLocaleString()}</p>
                        <p>Completed: {new Date(submission.completed_at).toLocaleString()}</p>
                    </div>
                    <Link href={`/${courseSlug}/${offeringSlug}/quiz/${quizSlug}/submissions/${submission.user_id}/`}>
                        <Button label="Grade Submission" size="small" />
                    </Link>
                </div>
            ))}
        </div>
    );
}
