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
    startTime: Date | null;
    endTime: Date | null;
}

function StaffQuizDisplayBadges(props: StaffQuizProps) {
    const duration = props.startTime && props.endTime ? Math.abs(differenceInMinutes(props.endTime, props.startTime)) : "N/A";

    return (
        <div style={{ position: "relative" }}>
            <span></span>
            <div style={{ position: "absolute", top: "10px", right: "10px", display: "flex", gap: "8px" }}>
                <Badge value={`${duration} mins`} severity="secondary" />
            </div>
        </div>
    );
}

function StaffQuizButton({ quizProps }: { quizProps: StaffQuizProps }) {
    return (
        <div style={{ position: "relative", display: "flex", flexDirection: "row-reverse" }}>
            <Link href={`/${quizProps.courseSlug}/${quizProps.offeringSlug}/quiz/${quizProps.quizSlug}/grade`}>
                <Button label="Grade Quiz" size="small" />
            </Link>
        </div>
    );
}

export default function StaffQuizDisplay(props: StaffQuizProps) {
    if (!props.startTime || !props.endTime) {
        return <Card title={props.name} subTitle="Invalid quiz data" className="bg-gray-50 dark:white shadow-md rounded-lg" />;
    }

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
            header={<StaffQuizDisplayBadges {...props} />}
            title={props.name}
            subTitle={`Start Time: ${props.startTime}`}
            className="bg-gray-50 dark:white shadow-md rounded-lg"
        />
    );
}

function OngoingQuizDisplay(props: StaffQuizProps) {
    return (
        <Card
            header={<StaffQuizDisplayBadges {...props} />}
            footer={<StaffQuizButton quizProps={props} />}
            title={props.name}
            subTitle={`Started at: ${props.startTime}`}
            className="bg-green-50 dark:white shadow-md rounded-lg"
        />
    );
}

function PastQuizDisplay(props: StaffQuizProps) {
    return (
        <Card
            header={<StaffQuizDisplayBadges {...props} />}
            footer={<StaffQuizButton quizProps={props} />}
            title={props.name}
            subTitle={`Ended on: ${props.endTime ?? "Unknown"}`}
            className="bg-gray-50 dark:white shadow-md rounded-lg"
        />
    );
}
