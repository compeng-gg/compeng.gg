import QuizDisplay, { QuizProps } from "@/app/[courseSlug]/[offeringSlug]/quiz/quiz-display";
import { fetchApi } from "@/app/lib/api";
import { JwtContext } from "@/app/lib/jwt-provider";
import { useContext, useEffect, useState } from "react";
import { Button } from "primereact/button";
import Link from "next/link";

export interface StaffQuizViewProps {
    courseSlug: string;
    offeringSlug: string;
}

export default function StaffQuizViewTab(props: StaffQuizViewProps) {
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [quizzes, setQuizzes] = useState<QuizProps[]>([]);

    async function fetchQuizzes() {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `quizzes/list/${props.courseSlug}`, "GET");
            const data = await res.json();
            const retQuizzes: QuizProps[] = data.map((quiz: any) => ({
                name: quiz.title,
                grade: undefined,
                quizSlug: quiz.slug,
                courseSlug: props.courseSlug,
                offeringSlug: props.offeringSlug,
                startTime: new Date(quiz.start_unix_timestamp * 1000),
                endTime: new Date(quiz.end_unix_timestamp * 1000),
            }));
            setQuizzes(retQuizzes);
        } catch (error) {
            console.error("Failed to retrieve quizzes", error);
        }
    }

    useEffect(() => {
        fetchQuizzes();
    }, [props.courseSlug]);

    function StaffQuizButton({ quizProps }: { quizProps: QuizProps }) {
        return (
            <div style={{ position: "relative", display: "flex", flexDirection: "row-reverse" }}>
                <Link href={`/${quizProps.courseSlug}/${quizProps.offeringSlug}/quiz/${quizProps.quizSlug}/grade`}>
                    <Button label="Grade Quiz" size="small" />
                </Link>
            </div>
        );
    }

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "10px", width: "100%" }}>
            {quizzes.length > 0 ? (
                quizzes.map((quiz) => (
                    <div key={quiz.quizSlug} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px", border: "1px solid #ccc", borderRadius: "8px" }}>
                        <QuizDisplay {...quiz} />
                        <StaffQuizButton quizProps={quiz} />
                    </div>
                ))
            ) : (
                <p>No quizzes available</p>
            )}
        </div>
    );
}
