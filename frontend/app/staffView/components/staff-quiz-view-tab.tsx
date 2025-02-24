import StaffQuizDisplay, { StaffQuizProps } from "@/app/[courseSlug]/[offeringSlug]/quiz/staff-quiz-display";
import { fetchApi } from "@/app/lib/api";
import { JwtContext } from "@/app/lib/jwt-provider";
import { useContext, useEffect, useState } from "react";

export interface StaffQuizViewProps {
    courseSlug: string;
    offeringSlug: string;
}

export default function StaffQuizViewTab(props: StaffQuizViewProps) {
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [quizzes, setQuizzes] = useState<StaffQuizProps[]>([]);
    const [loading, setLoading] = useState(true);

    async function fetchQuizzes() {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `quizzes/list/${props.courseSlug}`, "GET");
            const data = await res.json();

            if (!Array.isArray(data) || data.length === 0) {
                setQuizzes([]);
            } else {
                const retQuizzes: StaffQuizProps[] = data.map((quiz: any) => ({
                    name: quiz.title,
                    quizSlug: quiz.slug,
                    courseSlug: props.courseSlug,
                    offeringSlug: props.offeringSlug,
                    startTime: quiz.start_unix_timestamp ? new Date(quiz.start_unix_timestamp * 1000) : null,
                    endTime: quiz.end_unix_timestamp ? new Date(quiz.end_unix_timestamp * 1000) : null,
                }));
                setQuizzes(retQuizzes);
            }
        } catch (error) {
            console.error("Failed to retrieve quizzes", error);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchQuizzes();
    }, [props.courseSlug]);

    if (loading) return <p>Loading quizzes...</p>;
    if (quizzes.length === 0) return <p>No quizzes available.</p>;

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "10px", width: "100%" }}>
            {quizzes.map((quiz) => (
                <StaffQuizDisplay key={quiz.quizSlug} {...quiz} />
            ))}
        </div>
    );
}
