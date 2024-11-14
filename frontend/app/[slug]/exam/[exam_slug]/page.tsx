'use client';

import Navbar from "@/app/components/navbar";
import LoginRequired from "@/app/lib/login-required";
import { useEffect, useState } from "react";
import ExamDisplay, { ExamProps } from "../exam-display";
import { QuestionData, QuestionDisplay, QuestionProps, QuestionStatus, SubmissionStatus } from "../question-display";
import { Card } from "primereact/card";

const now = new Date()
const oneHourBefore = new Date(now.getTime() - 1*60*60*1000);
const twoHoursLater = new Date(now.getTime() + 2 * 60 * 60 * 1000); // Add 2 hours in milliseconds


const testExam : ExamProps = {
    name: "Term Test 2",
    courseSlug: "ece344",
    examSlug: "termTest2",
    startTime: oneHourBefore,
    endTime: twoHoursLater,
    grade: -1
}

const testQuestionData = [
  {
    title: "Print Pyramid",
    text: "Implement the outlined function pyramid(int n) which prints n layers of the character *.",
    starterCode: "void pyramid(int n){\n\n}",
    totalMarks: 3,
    isMutable: true
  },
  // {
  //   title: "Acyclic Linked List",
  //   text: "Given the node struct below, create an algorithm that returns true if the linked list is acyclic.",
  //   starterCode: "struct Node{\nstruct Node* next\nint val\nstruct Node(int input_val){\nval=input_val;\nnext=NULL\n};\n\nbool isAcyclic(struct Node* head){\n\n}",
  //   totalMarks: 5,
  //   isMutable: true
  // }
]


export default function Page({ params }: { params: { slug: string, exam_slug: string } }) {
    const {slug, exam_slug} = params;

    const [exam, setExam] = useState<ExamProps | undefined>(undefined);
    
    const [questionData, setQuestionData] = useState<QuestionData[]>([]);
    const [questionStates, setQuestionStates] = useState<QuestionStatus[]>([]);
    const [loaded, setLoaded] = useState<boolean>(false);
    useEffect(() => {
      if(!loaded){
        setQuestions(testQuestionData);
        setExam(testExam);
        setLoaded(true);
      }
    }, [loaded]);
    const getDefaultStatus = (data: QuestionData) => {
      return {
        currentText: data.starterCode,
        submissions: [],
        bestGrade: 0,
      } as QuestionStatus;
    }

    const setQuestions = (data: QuestionData[]) => {
      const states : QuestionStatus[] = data.map((d) => {return getDefaultStatus(d)});
      setQuestionStates(states);
      setQuestionData(data);
    }

    const setQuestionState = (idx: number, newStatus: QuestionStatus) => {
      const copy = JSON.parse(JSON.stringify(questionStates));
      copy[idx] = newStatus;
      setQuestionStates(copy);
    }

    //If exam not found
    if(!exam){
      return (
        <LoginRequired>
          <Navbar />

          <h3 style={{color: "red"}}>{`Exam ${exam_slug} not found for course ${slug}`}</h3>
        </LoginRequired>
      )
    }

    //If exam in future
    if(exam.startTime > now){
      return (
        <LoginRequired>
          <Navbar />
          <ExamDisplay {...exam}/>
        </LoginRequired>
      )
    }

    return (
      <LoginRequired>
        <Navbar />
        <h2>{exam.name}</h2>
        <div style={{display: "flex", gap: "10px", width: "100%", flexDirection: "column"}}>
            {questionData.map((data, idx) => (
                <QuestionDisplay data={data} status={questionStates[idx]} setStatus={(newStatus: QuestionStatus) => setQuestionState(idx, newStatus)}/>
            ))}
        </div>

      </LoginRequired>
    );
  }
