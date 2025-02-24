"use client";

import { useEffect, useState, useContext } from "react";
import { useParams } from "next/navigation";
import { fetchApi } from "@/app/lib/api";
import { JwtContext } from "@/app/lib/jwt-provider";
import Navbar from "@/app/components/navbar";
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
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [submissions, setSubmissions] = useState<Submission[]>([]);
    const [loading, setLoading] = useState(true);
    const [offeringName, setOfferingName] = useState(""); // Store offering name
    const [quizTitle, setQuizTitle] = useState(""); // Store quiz title

    async function fetchSubmissions() {
        try {
            const res = await fetchApi(
                jwt,
                setAndStoreJwt,
                `quizzes/admin/${courseSlug}/${quizSlug}/submissions/`,
                "GET"
            );
            if (!res.ok) {
                throw new Error("Failed to fetch submissions");
            }
            const data = await res.json();
            setSubmissions(data);
        } catch (error) {
            console.error("Failed to retrieve submissions", error);
            setSubmissions([]);
        } finally {
            setLoading(false);
        }
    }

    async function fetchQuizInfo() {
        try {
            const res = await fetchApi(
                jwt,
                setAndStoreJwt,
                `quizzes/admin/${courseSlug}/${quizSlug}/`, // Assuming API exists for fetching quiz details
                "GET"
            );
            if (!res.ok) {
                throw new Error("Failed to fetch quiz details");
            }
            const data = await res.json();
            setOfferingName(data.offering_name); // Example: "2024 Fall ECE344"
            setQuizTitle(data.title); // Example: "Midterm Quiz"
        } catch (error) {
            console.error("Failed to retrieve quiz info", error);
        }
    }

    useEffect(() => {
        fetchSubmissions();
        fetchQuizInfo();
    }, [courseSlug, quizSlug, jwt, setAndStoreJwt]);

    if (loading) {
        return (
            <>
                <Navbar />
                <p>Loading submissions...</p>
            </>
        );
    }

    return (
        <>
            <Navbar />
            <div style={{ padding: "20px" }}>
                {/* Page Title */}
                // TODO: Add Offering name to the page title
                <h1>{offeringName || "Offering Name Here..."}</h1>
                <h2>{quizTitle || "Loading quiz..."}</h2>

                {/* Quiz Submissions List */}
                <h3>Quiz Submissions</h3>

                {submissions.length === 0 ? (
                    <p>No submissions found.</p>
                ) : (
                    <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
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
                                <Link href={`/${courseSlug}/${offeringSlug}/quiz/${quizSlug}/${submission.user_id}/`}>
                                    <Button label="Grade Submission" size="small" />
                                </Link>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </>
    );
}
