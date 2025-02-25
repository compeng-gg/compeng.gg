"use client";

import { useEffect, useState, useContext } from "react";
import { useParams } from "next/navigation";
import { fetchApi } from "@/app/lib/api";
import { JwtContext } from "@/app/lib/jwt-provider";
import Navbar from "@/app/components/navbar";
import { Button } from "primereact/button";
import { Badge } from "primereact/badge";
import Link from "next/link";

interface Submission {
    user_id: number;
    username: string;
    started_at: string;
    completed_at: string;
    grade: number | null;
}

export default function QuizSubmissionsPage() {
    const { courseSlug, offeringSlug, quizSlug } = useParams();
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [submissions, setSubmissions] = useState<Submission[]>([]);
    const [loading, setLoading] = useState(true);
    const [offeringName, setOfferingName] = useState("");
    const [quizTitle, setQuizTitle] = useState("");
    const [totalPoints, setTotalPoints] = useState<number>(0); // Store total points

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
            setSubmissions(data.submissions);
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
                `quizzes/admin/${courseSlug}/${quizSlug}/`, 
                "GET"
            );
            if (!res.ok) {
                throw new Error("Failed to fetch quiz details");
            }
            const data = await res.json();
            setOfferingName(data.offering_name);
            setQuizTitle(data.title);
            setTotalPoints(data.total_points); // Get total points from API
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
                <h1>{offeringName || "ECE344 Fall 2024"}</h1>
                <h2>{quizTitle || "Loading quiz..."}</h2>

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
                                position: "relative"
                            }}>
                                {/* Left: Submission Details */}
                                <div>
                                    <p><strong>{submission.username}</strong></p>
                                    <p>Started: {new Date(submission.started_at).toLocaleString()}</p>
                                    <p>Completed: {new Date(submission.completed_at).toLocaleString()}</p>
                                </div>

                                {/* Right: Grade Display */}
                                <Badge 
                                    size="large" 
                                    severity="info" 
                                    value={submission.grade !== null ? 
                                        `Grade: ${submission.grade}/${totalPoints}` : 
                                        `Grade: Ungraded/${totalPoints}`} 
                                    style={{ position: "absolute", top: "10px", right: "10px" }}
                                />

                                {/* Right: Grade Submission Button */}
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
