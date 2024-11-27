import { Badge } from "primereact/badge";
import { Card } from "primereact/card";
import { start } from "repl";
import {differenceInMinutes} from "date-fns";
import { Button } from "primereact/button";
import { Router } from "next/router";
import Link from "next/link";

export interface ExamProps {
    name: string;
    courseSlug: string;
    slug: string;
    startTime: Date;
    endTime: Date;
    grade?: number;
}

function ExamDisplayBadges(props: ExamProps){
    const {grade} = props;
    const duration = Math.abs(differenceInMinutes(props.endTime, props.startTime));

    const gradeString = (grade) ? `Grade: ${grade}%` : "Ungraded";
    return (
        <div style={{ position: 'relative'}}>
            <span></span>
            <div style={{ position: 'absolute', top: '10px', right: '10px', display: 'flex', gap: '8px' }}>
                <Badge value={gradeString} severity={"success"} />
                <Badge value={`${duration} mins`} severity="secondary" />
            </div>
        </div>
    );
}

function ExamVisitButton({buttonText, examProps}: {buttonText: string, examProps: ExamProps}){
    return (
        <div style={{ position: 'relative', display: "flex", flexDirection: "row-reverse", }}>
            <span></span>
            <Link href={`/${examProps.courseSlug}/exam/${examProps.slug}`}>
                <Button label={buttonText} size="small"/>
            </Link>
        </div>
    )
    
}

export default function ExamDisplay(props: ExamProps){

    const now = new Date();

    //Determine if exam is past, present or future

    if(now <= props.startTime){
        return UpcomingExamDisplay(props);
    } else if (now <= props.endTime){
        return OngoingExamDisplay(props);
    } else {
        return PastExamDisplay(props);
    }
}


function UpcomingExamDisplay(props: ExamProps){
    return (
        <Card
            header={<ExamDisplayBadges {...props} />}
            title={props.name}
            subTitle={`Start Time: ${props.startTime}`}
            className="bg-gray-50 dark:white shadow-md rounded-lg"
        />
    )
}

function OngoingExamDisplay(props: ExamProps){
    return (
        <Card
            header={<ExamDisplayBadges {...props} />}
            footer={<ExamVisitButton examProps={props} buttonText={"Write Exam"}/>}
            title={props.name}
            subTitle={`Started at: ${props.startTime}`}
            className="bg-green-50 dark:white shadow-md rounded-lg"
        />
    )
}

function PastExamDisplay(props: ExamProps){
    return (
        <Card
            header={<ExamDisplayBadges {...props} />}
            footer={<ExamVisitButton examProps={props} buttonText={"View Submission"}/>}
            title={props.name}
            subTitle={`Ended on: ${props.endTime}`}
            className="bg-gray-50 dark:white shadow-md rounded-lg"
        />
    )
}