import ExamDisplay, { ExamProps } from "@/app/[courseSlug]/exam/exam-display";
import { fetchApi } from "@/app/lib/api";
import { JwtContext } from "@/app/lib/jwt-provider";
import { useContext, useEffect } from "react";

const now = new Date()
const oneHourBefore = new Date(now.getTime() - 1*60*60*1000);
const twoHoursLater = new Date(now.getTime() + 2 * 60 * 60 * 1000); // Add 2 hours in milliseconds



const availableExams : ExamProps[] = [
    {
        name: "Term Test 1",
        courseSlug: "ece344",
        examSlug: "termTest1",
        startTime: new Date(2024, 10, 10, 12),
        endTime:  new Date(2024, 10, 10, 13, 30),
        grade: 68
    },
    {
        name: "Term Test 2",
        courseSlug: "ece344",
        examSlug: "termTest2",
        startTime: now,
        endTime: twoHoursLater,
        grade: -1
    },
    {
        name: "Final",
        courseSlug: "ece344",
        examSlug: "final",
        startTime: new Date(2024, 12, 10, 12),
        endTime:  new Date(2024, 12, 10, 13, 30),
        grade: -1
    },
]//meow

export interface StudentExamViewProps {
    courseSlug: string;
}

export default function StudentExamViewTab(props: StudentExamViewProps){
    const [jwt, setAndStoreJwt] = useContext(JwtContext);

    async function fetchExams() {
        try {
            console.log("EXAMS")
            const res = await fetchApi(jwt, setAndStoreJwt, `assessments/list/${props.courseSlug}`, "GET");
            const data = await res.json();
            const exams : ExamProps[] =[]
            data.forEach(exam => {
                exams.push(exam as ExamProps);
            });
            console.log(JSON.stringify(exams, null, 2));

        } catch (error) {
            console.error("Failed to retrieve teams", error);
        }
    }

    useEffect(() => {
        fetchExams()
    }, [props.courseSlug])
    return (
        <div style={{display: "flex", gap: "10px", width: "100%", flexDirection: "column"}}>
            {availableExams.map((exam) => (
                <ExamDisplay {...exam}/>
            ))}
        </div>
    )
}