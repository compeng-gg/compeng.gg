import QuizDisplay, { QuizProps } from "@/app/[courseSlug]/[offeringSlug]/quiz/quiz-display";
import { fetchApi } from "@/app/lib/api";
import { JwtContext } from "@/app/lib/jwt-provider";
import { useContext, useEffect, useState } from "react";

const now = new Date()
const oneHourBefore = new Date(now.getTime() - 1*60*60*1000);
const twoHoursLater = new Date(now.getTime() + 2 * 60 * 60 * 1000); // Add 2 hours in milliseconds

export interface StudentQuizViewProps {
    courseSlug: string;
    offeringSlug: string;
}

export default function StudentQuizViewTab(props: StudentQuizViewProps){
    const [jwt, setAndStoreJwt] = useContext(JwtContext);

    const [quizzes, setQuizs] = useState<QuizProps[]>([]);
    async function fetchQuizs() {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `quizzes/list/${props.courseSlug}`, "GET");
            const data = await res.json();
            const retQuizs : QuizProps[] = [];
            data.forEach(quiz => {
                retQuizs.push({
                    name: quiz.title,
                    grade: undefined,
                    quizSlug: quiz.slug,
                    courseSlug: props.courseSlug,
                    offeringSlug: props.offeringSlug,
                    startTime: new Date(quiz.start_unix_timestamp*1000),
                    endTime: new Date(quiz.end_unix_timestamp*1000)
                })
            });
            setQuizs(retQuizs);
        } catch (error) {
            console.error("Failed to retrieve teams", error);
        }
    }

    useEffect(() => {
        fetchQuizs()
    }, [props.courseSlug])
    return (
        <div style={{display: "flex", gap: "10px", width: "100%", flexDirection: "column"}}>
            {quizzes.map((quiz) => (
                <QuizDisplay {...quiz} key={quiz.quizSlug}/>
            ))}
        </div>
    )
}