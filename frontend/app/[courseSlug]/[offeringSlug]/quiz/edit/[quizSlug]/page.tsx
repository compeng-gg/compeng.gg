'use client';

import { useContext, useEffect, useState } from "react";
import { QuestionData } from "../../question-models";
import { QuizProps } from "../../quiz-display";
import { JwtContext } from "@/app/lib/jwt-provider";
import { fetchApi } from "@/app/lib/api";
import { getQuestionDataFromRaw } from "../../quiz-utilities";
import { id, se } from "date-fns/locale";
import Navbar from "@/app/components/navbar";
import LoginRequired from "@/app/lib/login-required";
import QuestionEditor from "../components/question-editor";



export default function Page({ params }: { params: { courseSlug: string, quizSlug: string } }) {

    const { courseSlug, quizSlug } = params;
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [quiz, setQuiz] = useState<QuizProps | undefined>(undefined);
    const [questionData, setQuestionData] = useState<StaffQuestionData[]>([]);
    const [loaded, setLoaded] = useState<boolean>(false);

    async function fetchQuiz() {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `${courseSlug}/quiz/${quizSlug}`, "GET");
            const data = await res.json();
            const retQuiz: QuizProps = {
                startTime: new Date(data.start_unix_timestamp * 1000),
                endTime: new Date(data.end_unix_timestamp * 1000),
                quizSlug: quizSlug,
                name: data.title,
                courseSlug: courseSlug
            }
            setQuiz(retQuiz);
            console.log("Quiz" + JSON.stringify(data, null, 2));
            setQuestionData((data.questions.map((rawData: any) => getQuestionDataFromRaw(rawData, quizSlug, courseSlug, true))));
        } catch (error) {
            console.error("Failed to retrieve quiz", error);
        }
    }

    useEffect(() => {
        if (!loaded) {
            fetchQuiz();
            setLoaded(true);
        }
    }, [loaded]);

    const setQuestionDataAtIdx = (idx: number, data: QuestionData) => {
        setQuestionData(prevData => {
            const newData = [...prevData];
            newData[idx] = data;
            return newData;
        });
    }

    if (!loaded) {
        return (
            <LoginRequired>
                <Navbar />

                <h3 style={{ color: "yellow" }}>{`Loading quiz ${quizSlug}...`}</h3>
            </LoginRequired>
        )
    }

    if (!quiz) {
        return (
            <LoginRequired>
                <Navbar />

                <h3 style={{ color: "yellow" }}>{`quiz ${quizSlug} not found for course ${courseSlug}`}</h3>
            </LoginRequired>
        )
    }
    console.log("Returning editor")
    return (
        <LoginRequired>
            <Navbar />
            <h2>{quiz?.name}</h2>
            <div style={{ display: "flex", gap: "10px", width: "100%", flexDirection: "column" }}>
                {questionData.map((data, idx) => (
                    <QuestionEditor questionData={data} setQuestionData={(newData) => setQuestionDataAtIdx(idx, newData)} idx={idx}/>
                ))}
            </div>
        </LoginRequired>
    )


}