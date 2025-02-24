import { Badge } from "primereact/badge";
import { Card } from "primereact/card";
import { differenceInMinutes } from "date-fns";
import { Button } from "primereact/button";
import Link from "next/link";

export interface StaffQuizProps {
    name: string;
    courseSlug: string;
    offeringSlug: string;
    quizSlug: string;
    startTime: Date;
    endTime: Date;
}

function QuizDisplayBadges(props: StaffQuizProps) {
    const duration = Math.abs(differenceInMinutes(props.endTime, props.startTime));

    return (
        <div style={{ position: "relative" }}>
            <span></span>
            <div style={{ position: "absolute", top: "10px", right: "10px", display: "flex", gap: "8px" }}>
                <Badge value={`${duration} mins`} severity="secondary" />
            </div>
        </div>
    );
}

function QuizGradeButton({ quizProps }: { quizProps: StaffQuizProps }) {
    return (
        <div style={{ position: "relative", display: "flex", flexDirection: "row-reverse" }}>
            <Link href={`/${quizProps.courseSlug}/${quizProps.offeringSlug}/quiz/${quizProps.quizSlug}/grade`}>
                <Button label="Grade Quiz" size="small" />
            </Link>
        </div>
    );
}

export default function QuizDisplayStaff(props: StaffQuizProps) {
    const now = new Date();

    if (now <= props.startTime) {
        return UpcomingQuizDisplay(props);
    } else if (now <= props.endTime) {
        return OngoingQuizDisplay(props);
    } else {
        return PastQuizDisplay(props);
    }
}

function UpcomingQuizDisplay(props: StaffQuizProps) {
    return (
        <Card
            header={<QuizDisplayBadges {...props} />}
            title={props.name}
            subTitle={`Start Time: ${props.startTime}`}
            className="bg-gray-50 dark:white shadow-md rounded-lg"
        />
    );
}

function OngoingQuizDisplay(props: StaffQuizProps) {
    return (
        <Card
            header={<QuizDisplayBadges {...props} />}
            title={props.name}
            subTitle={`Started at: ${props.startTime}`}
            className="bg-green-50 dark:white shadow-md rounded-lg"
        />
    );
}

function PastQuizDisplay(props: StaffQuizProps) {
    return (
        <Card
            header={<QuizDisplayBadges {...props} />}
            footer={<QuizGradeButton quizProps={props} />}
            title={props.name}
            subTitle={`Ended on: ${props.endTime}`}
            className="bg-gray-50 dark:white shadow-md rounded-lg"
        />
    );
}
