'use client';

import { useContext, useEffect, useState } from "react";
import { QuestionData, StaffQuestionData } from "../../question-models";
import { QuizProps } from "../../quiz-display";
import { JwtContext } from "@/app/lib/jwt-provider";
import { fetchApi } from "@/app/lib/api";
import { getQuestionDataFromRaw } from "../../quiz-utilities";
import { id, se } from "date-fns/locale";
import Navbar from "@/app/components/navbar";
import LoginRequired from "@/app/lib/login-required";
import QuestionEditor from "../components/question-editor";
import { QuizSettingsEditor } from "../components/quiz-settings-editor";
import { Button } from "primereact/button";



export default function Page({ params }: { params: { courseSlug: string, quizSlug: string } }) {

    const { courseSlug, quizSlug } = params;
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [quiz, setQuiz] = useState<QuizProps | undefined>(undefined);
    const [questionData, setQuestionData] = useState<StaffQuestionData[]>([]);
    const [loaded, setLoaded] = useState<boolean>(false);
    const [modified, setModified] = useState<boolean>(false);
    
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

    const addQuestion= () => {
        const newQuestion = {
            id: "set_on_server",
            quizSlug: quizSlug,
            courseSlug: courseSlug,
            prompt: "",
            totalMarks: 0,
            isMutable: true,
            questionType: "TEXT",
            serverQuestionType: "WRITTEN_RESPONSE"
        } as StaffQuestionData;
        setQuestionData(prevData => [...prevData, newQuestion]);
    
    }

    useEffect(() => {
        if (!loaded) {
            fetchQuiz();
            setLoaded(true);
        }
    }, [loaded]);

    const setQuestionDataAtIdx = (idx: number, data: StaffQuestionData) => {
        setModified(true);
        setQuestionData(prevData => {
            const newData = [...prevData];
            newData[idx] = data;
            return newData;
        });
    }

    const setQuizPropsCustom = (newProps: QuizProps) => {
        setModified(true);
        setQuiz(newProps);
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
    return (
        <LoginRequired>
            <Navbar />
            <QuizEditorTopbar quiz={quiz} questionData={questionData} modified={modified} setModified={setModified} />
            <div style={{ display: "flex", gap: "10px", width: "100%", flexDirection: "column" }}>
                <QuizSettingsEditor quizProps={quiz} setQuizProps={(newProps) => setQuizPropsCustom(newProps)} />
                {questionData.map((data, idx) => (
                    <QuestionEditor questionData={data} setQuestionData={(newData) => setQuestionDataAtIdx(idx, newData)} idx={idx}/>
                ))}
                <AddQuestionButton addQuestion={addQuestion}/>
            </div>
        </LoginRequired>
    )
}

interface QuizEditorTopbarProps {
    quiz: QuizProps;
    questionData: StaffQuestionData[];
    modified: boolean;
    setModified: (newVal: boolean) => void;
}

function QuizEditorTopbar(props: QuizEditorTopbarProps) {
    const { quiz, questionData, modified, setModified } = props;

    return (
        <div className="sticky_header">
        <div style={{ display: "flex", flexDirection: "row", justifyContent: "space-between", alignItems: "center"}}>
            <div> 
                <h2>{`Editing ${quiz.name}`}</h2>
            </div>
            <div style={{display: "flex", height: "70%", flexDirection: "row", gap: "3px"}}>
                <Button icon="pi pi-save" label={modified ? "Save": "No Changes"} disabled={!modified} raised={modified} />
                <Button icon="pi pi-undo" label="Undo Changes" disabled={!modified} severity="secondary"/>
                <Button icon="pi pi-trash" label="Delete Quiz" severity="danger"/>
            </div>
        </div>
        </div>
    )
}

function AddQuestionButton({ addQuestion }: { addQuestion: () => void }) {
    return (
        <Button label="Add Question" onClick={addQuestion} />
    )
}