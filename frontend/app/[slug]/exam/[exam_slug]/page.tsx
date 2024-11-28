'use client';

import Navbar from "@/app/components/navbar";
import LoginRequired from "@/app/lib/login-required";
import { useContext, useEffect, useState } from "react";
import ExamDisplay, { ExamProps } from "../exam-display";
import { BaseQuestionData, CodeQuestionData, QuestionData, QuestionProps, QuestionState, QuestionType, SelectQuestionData, ServerToLocal, TextQuestionData } from "../question-models";
import { Card } from "primereact/card";
import { QuestionDisplay } from "../question-display";
import { fetchApi } from "@/app/lib/api";
import { JwtContext } from "@/app/lib/jwt-provider";

const now = new Date()
const oneHourBefore = new Date(now.getTime() - 1 * 60 * 60 * 1000);
const twoHoursLater = new Date(now.getTime() + 2 * 60 * 60 * 1000); // Add 2 hours in milliseconds


const testExam: ExamProps = {
  name: "Term Test 2",
  courseSlug: "ece344",
  examSlug: "termTest2",
  startTime: oneHourBefore,
  endTime: twoHoursLater,
  grade: -1
}

const testQuestionData: QuestionData[] = [
  {
    questionType: "CODE",
    title: "Print Pyramid",
    text: "Implement the outlined function pyramid(int n) which prints n layers of the character *.",
    starterCode: "void pyramid(int n){\n\n}",
    totalMarks: 3,
    isMutable: true
  },
  {
    questionType: "CODE",
    title: "Acyclic Linked List",
    text: "Given the node struct below, create an algorithm that returns true if the linked list is acyclic.",
    starterCode: "struct Node{\n\tstruct Node* next\n\tint val\n\n\tstruct Node(int input_val){\n\t\tval=input_val;\n\t\tnext=NULL\n\t}\n};\n\nbool isAcyclic(struct Node* head){\n\n}",
    totalMarks: 5,
    isMutable: true
  },
  {
    questionType: "TEXT",
    title: "Segmentation Fault",
    text: "Explain what could cause a segmentation fault",
    totalMarks: 2,
    isMutable: true
  },
  {
    questionType: "SELECT",
    title: "Compilation",
    text: "Of the following options, which one will break compilation if added to a struct",
    totalMarks: 1,
    isMutable: true,
    options: [
      "int a", "int* a", "int& a"
    ]
  }
]


export default function Page({ params }: { params: { slug: string, exam_slug: string } }) {
  const { slug, exam_slug } = params;
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const [exam, setExam] = useState<ExamProps | undefined>(undefined);

  const [loaded, setLoaded] = useState<boolean>(false);
  const [questionData, setQuestionData] = useState<QuestionData[]>([]);
  const [questionStates, setQuestionStates] = useState<QuestionState[]>([]);

  

  async function fetchExam() {
    try {
      const res = await fetchApi(jwt, setAndStoreJwt, `assessments/${exam_slug}`, "GET");
      const data = await res.json();
      console.log(JSON.stringify(data, null, 2));
      const retExam: ExamProps = {
        startTime: new Date(data.start_unix_timestamp * 1000),
        endTime: new Date(data.end_unix_timestamp * 1000),
        slug: exam_slug,
        name: data.title,
        courseSlug: slug
      }
      setExam(retExam);
      const qData = data.questions.map((rawData) =>  getQuestionDataFromRaw(rawData, exam_slug));
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
      console.error("Failed to retrieve exam", error);
    }
  }

  useEffect(() => {
    if (!loaded) {
      fetchExam();
      setLoaded(true);
    }
  }, [loaded]);
  //If exam not found
  if (!exam) {
    return (
      <LoginRequired>
        <Navbar />

        <h3 style={{ color: "red" }}>{`Exam ${exam_slug} not found for course ${slug}`}</h3>
      </LoginRequired>
    )
  }

  //If exam in future
  if (exam.startTime > now) {
    return (
      <LoginRequired>
        <Navbar />
        <ExamDisplay {...exam} />
      </LoginRequired>
    )
  }

  return (
    <LoginRequired>
      <Navbar />
      <h2>{exam.name}</h2>
      <div style={{ display: "flex", gap: "10px", width: "100%", flexDirection: "column" }}>
        {questionStates.map((state, idx) => (
          <QuestionDisplay {...questionData[idx]} state={state} idx={idx}/>
        ))}
      </div>

    </LoginRequired>
  );
}

function getQuestionDataFromRaw(rawData: any, assessment_slug: string): any {
  const baseData: BaseQuestionData = {
    id: rawData.id,
    assessment_slug: assessment_slug,
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


