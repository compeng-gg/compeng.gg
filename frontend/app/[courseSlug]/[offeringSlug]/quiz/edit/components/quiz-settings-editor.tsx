import { Calendar } from "primereact/calendar";
import { QuizProps } from "../../quiz-display";
import { InputText } from "primereact/inputtext";
import { LabelledField } from "./question-editor";
import React from "react";

export interface QuizSettingsEditorProps {
    quizProps: QuizProps;
    setQuizProps: (quizProps: QuizProps) => void;
}


export function QuizSettingsEditor(props: QuizSettingsEditorProps) {
    const { quizProps, setQuizProps } = props;
    const [repoUrl, setRepoUrl] = React.useState<string>("");
    return (
        <div style={{display: "flex", flexDirection: "column", gap: "10px"}}>
            <LabelledField label="Quiz Name" id="quizName">
                <InputText id="quizName" value={quizProps.name} onChange={(e) => setQuizProps({ ...quizProps, name: e.target.value })} />
            </LabelledField>
            <LabelledField label="Start Time" id="start-time">
                <Calendar value={quizProps.startTime} onChange={(e) => setQuizProps({ ...quizProps, startTime: e.value ?? new Date() })} showTime />
            </LabelledField>
            <LabelledField label="End Time" id="end-time">
                <Calendar value={quizProps.endTime} onChange={(e) => setQuizProps({ ...quizProps, endTime: e.value ?? new Date()})} showTime />
            </LabelledField>
            <LabelledField label="Github Repository URL" id="ghurl">
                <InputText id="ghurl" value={repoUrl} onChange={(e) => setRepoUrl(e.target.value)}
                    tooltip="Github repository that contains the grading scripts"/>
            </LabelledField>
        </div>
    )

}