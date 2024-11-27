'use client';

import Navbar from "@/app/components/navbar";
import LoginRequired from "@/app/lib/login-required";
import { useEffect, useState } from "react";
import ExamDisplay, { ExamProps } from "../exam-display";
import { CodeQuestionData, QuestionData, QuestionProps, QuestionState } from "../question-models";
import { Card } from "primereact/card";
import { QuestionDisplay } from "../question-display";

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

  const [exam, setExam] = useState<ExamProps | undefined>(undefined);

  const [loaded, setLoaded] = useState<boolean>(false);
  const questions = useInitializeQuestionStates(testQuestionData);

  useEffect(() => {
    if (!loaded) {
      setExam(testExam);
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
        {questions.map((state, idx) => (
          <QuestionDisplay {...testQuestionData[idx]} state={state}/>
        ))}
      </div>

    </LoginRequired>
  );
}

function getDefaultStateValue(questionData: QuestionData): any {
  switch (questionData.questionType) {
      case "CODE":
          return (questionData as CodeQuestionData).starterCode || "";
      case "SELECT":
          return -1; // Default to no option selected
      case "TEXT":
          return "";
      default:
          throw new Error(`Unsupported question type: ${JSON.stringify(questionData)}`);
  }
}


export function useInitializeQuestionStates(questionDataList: QuestionData[]) {
  return questionDataList.map((questionData) => {
    const [value, setValue] = useState(() => getDefaultStateValue(questionData));

    return {
      value,
      setValue,
    };
  });
}
