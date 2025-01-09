'use client';

import Navbar from "@/app/components/navbar";
import LoginRequired from "@/app/lib/login-required";
import { useContext, useEffect, useState } from "react";
import QuizDisplay, { QuizProps } from "../quiz-display";
import { BaseQuestionData, CodeQuestionData, QuestionData, QuestionProps, QuestionState, QuestionType, SelectQuestionData, ServerToLocal, TextQuestionData } from "../question-models";
import { Card } from "primereact/card";
import { QuestionDisplay } from "../question-display";
import { fetchApi } from "@/app/lib/api";
import { JwtContext } from "@/app/lib/jwt-provider";

const now = new Date()
const oneHourBefore = new Date(now.getTime() - 1 * 60 * 60 * 1000);
const twoHoursLater = new Date(now.getTime() + 2 * 60 * 60 * 1000); // Add 2 hours in milliseconds


export default function Page({ params }: { params: { courseSlug: string, examSlug: string } }) {
  console.log("params", params)
  const { courseSlug, examSlug } = params;
  console.log(courseSlug, examSlug)
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [quiz, setQuiz] = useState<QuizProps | undefined>(undefined);

  const [loaded, setLoaded] = useState<boolean>(false);
  const [questionData, setQuestionData] = useState<QuestionData[]>([]);
  const [questionStates, setQuestionStates] = useState<QuestionState[]>([]);

  

  async function fetchQuiz() {
    try {
      const res = await fetchApi(jwt, setAndStoreJwt, `${courseSlug}/quiz/${examSlug}`, "GET");
      const data = await res.json();
      console.log(JSON.stringify(data, null, 2));
      const retQuiz: QuizProps = {
        startTime: new Date(data.start_unix_timestamp * 1000),
        endTime: new Date(data.end_unix_timestamp * 1000),
        examSlug: examSlug,
        name: data.title,
        courseSlug: courseSlug
      }
      setQuiz(retQuiz);
      const qData = data.questions.map((rawData) =>  getQuestionDataFromRaw(rawData, examSlug, courseSlug));
      setQuestionData(qData);
      console.log("qdata:", JSON.stringify(qData, null, 2));
      const questionStates = qData.map((questionData, idx) => ({
        value: getStartingStateValue(questionData, data.questions[idx]),
        setValue: (newValue) => {
          setQuestionStates((questionStates) => 
            questionStates.map((state, currIdx) => currIdx == idx ? {...state, value: newValue} : state)
          )
        }
      }));
      setQuestionStates(questionStates);

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
  //If quiz not found
  if (!quiz) {
    return (
      <LoginRequired>
        <Navbar />

        <h3 style={{ color: "red" }}>{`quiz ${examSlug} not found for course ${courseSlug}`}</h3>
      </LoginRequired>
    )
  }

  //If quiz in future
  if (quiz.startTime > now) {
    return (
      <LoginRequired>
        <Navbar />
        <QuizDisplay {...quiz} />
      </LoginRequired>
    )
  }

  return (
    <LoginRequired>
      <Navbar />
      <h2>{quiz.name}</h2>
      <div style={{ display: "flex", gap: "10px", width: "100%", flexDirection: "column" }}>
        {questionStates.map((state, idx) => (
          <QuestionDisplay {...questionData[idx]} state={state} idx={idx}/>
        ))}
      </div>

    </LoginRequired>
  );
}

function getQuestionDataFromRaw(rawData: any, examSlug: string, courseSlug: string): any {
  const baseData: BaseQuestionData = {
    id: rawData.id,
    examSlug: examSlug,
    courseSlug: courseSlug,
    prompt: rawData.prompt,
    serverQuestionType: rawData.question_type,
    questionType: ServerToLocal.get(rawData.question_type) as QuestionType  ?? "TEXT",
    isMutable: true,
    totalMarks: rawData.points
  }
  switch (baseData.questionType) {
    case "CODE":
      return {
        ...baseData,
        starterCode: rawData.starter_code, programmingLanguage: rawData.programming_language
      } as CodeQuestionData
    case "SELECT":
      return {
        ...baseData,
        options: rawData.options
      } as SelectQuestionData
    case "TEXT":
      return {
        ...baseData,
      } as TextQuestionData
    default:
      throw new Error(`Unsupported question type: ${JSON.stringify(questionData)}`);
  }
}

function getStartingStateValue(questionData: QuestionData, rawData: any): any {
  switch (questionData.questionType) {
    case "CODE":
      return (rawData.solution) ?? ((questionData as CodeQuestionData).starterCode || "");
    case "SELECT":
      return (rawData.selected_answer_index) ?? -1; // Default to no option selected
    case "TEXT":
      return (rawData.response) ?? "";
    default:
      throw new Error(`Unsupported question type: ${JSON.stringify(questionData)}`);
  }
}


