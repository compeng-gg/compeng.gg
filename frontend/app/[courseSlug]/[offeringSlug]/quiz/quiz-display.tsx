import { Badge } from 'primereact/badge';
import { Card } from 'primereact/card';
import { start } from 'repl';
import {differenceInMinutes} from 'date-fns';
import { Button } from 'primereact/button';
import { Router } from 'next/router';
import Link from 'next/link';

export interface QuizProps {
    name: string;
    courseSlug: string;
    offeringSlug: string;
    quizSlug: string;
    startTime: Date;
    endTime: Date;
    grade: number;
}

function QuizDisplayBadges(props: QuizProps){
    const {grade} = props;
    const duration = Math.abs(differenceInMinutes(props.endTime, props.startTime));

    const gradeString = (grade) ? `Grade: ${grade}%` : 'Ungraded';
    return (
        <div style={{ position: 'relative'}}>
            <span></span>
            <div style={{ position: 'absolute', top: '10px', right: '10px', display: 'flex', gap: '8px' }}>
                <Badge value={gradeString} severity={'success'} />
                <Badge value={`${duration} mins`} severity="secondary" />
            </div>
        </div>
    );
}

function QuizVisitButton({buttonText, quizProps}: {buttonText: string, quizProps: QuizProps}){
    return (
        <div style={{ position: 'relative', display: 'flex', flexDirection: 'row-reverse', }}>
            <span></span>
            <Link href={`/${quizProps.courseSlug}/${quizProps.offeringSlug}/quiz/${quizProps.quizSlug}`}>
                <Button label={buttonText} size="small"/>
            </Link>
        </div>
    );
    
}

export default function QuizDisplay(props: QuizProps){

    const now = new Date();

    //Determine if quiz is past, present or future

    if(now <= props.startTime){
        return UpcomingQuizDisplay(props);
    } else if (now <= props.endTime){
        return OngoingQuizDisplay(props);
    } else {
        return PastQuizDisplay(props);
    }
}


function UpcomingQuizDisplay(props: QuizProps){
    return (
        <Card
            header={<QuizDisplayBadges {...props} />}
            title={props.name}
            subTitle={`Start Time: ${props.startTime}`}
            className="bg-gray-50 dark:white shadow-md rounded-lg"
        />
    );
}

function OngoingQuizDisplay(props: QuizProps){
    return (
        <Card
            header={<QuizDisplayBadges {...props} />}
            footer={<QuizVisitButton quizProps={props} buttonText={'Write quiz'}/>}
            title={props.name}
            subTitle={`Started at: ${props.startTime}`}
            className="bg-green-50 dark:white shadow-md rounded-lg"
        />
    );
}

function PastQuizDisplay(props: QuizProps){
    return (
        <Card
            header={<QuizDisplayBadges {...props} />}
            footer={<QuizVisitButton quizProps={props} buttonText={'View Submission'}/>}
            title={props.name}
            subTitle={`Ended on: ${props.endTime}`}
            className="bg-gray-50 dark:white shadow-md rounded-lg"
        />
    );
}