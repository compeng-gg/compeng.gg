import ExamDisplay, { ExamProps } from "@/app/[courseSlug]/exam/exam-display";
import { fetchApi } from "@/app/lib/api";
import { JwtContext } from "@/app/lib/jwt-provider";
import { useContext, useEffect, useState } from "react";

const now = new Date()
const oneHourBefore = new Date(now.getTime() - 1*60*60*1000);
const twoHoursLater = new Date(now.getTime() + 2 * 60 * 60 * 1000); // Add 2 hours in milliseconds

export interface StudentExamViewProps {
    courseSlug: string;
}

export default function StudentExamViewTab(props: StudentExamViewProps){
    const [jwt, setAndStoreJwt] = useContext(JwtContext);

    const [exams, setExams] = useState<ExamProps[]>([]);
    async function fetchExams() {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `exams/list/${props.courseSlug}`, "GET");
            const data = await res.json();
            const retExams : ExamProps[] = [];
            data.forEach(exam => {
                retExams.push({
                    name: exam.title,
                    grade: undefined,
                    slug: exam.slug,
                    courseSlug: props.courseSlug,
                    startTime: new Date(exam.start_unix_timestamp*1000),
                    endTime: new Date(exam.end_unix_timestamp*1000)
                })
            });
            console.log(JSON.stringify(data, null, 2));
            setExams(retExams);
            console.log(JSON.stringify(retExams, null, 2));

        } catch (error) {
            console.error("Failed to retrieve teams", error);
        }
    }

    useEffect(() => {
        fetchExams()
    }, [props.courseSlug])
    return (
        <div style={{display: "flex", gap: "10px", width: "100%", flexDirection: "column"}}>
            {exams.map((exam) => (
                <ExamDisplay {...exam} key={exam.slug}/>
            ))}
        </div>
    )
}