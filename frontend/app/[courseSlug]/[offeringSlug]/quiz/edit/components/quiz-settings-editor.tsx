import { Calendar } from 'primereact/calendar';
import { QuizProps } from '../../quiz-display';
import { InputText } from 'primereact/inputtext';
import { LabelledField } from './question-editor';
import React from 'react';
import { Checkbox } from 'primereact/checkbox';
export interface StaffQuizProps {
    name: string;
    courseSlug: string;
    quizSlug: string;
    startTime: Date;
    endTime: Date;
    visibleAt: Date;
    releaseTime: Date;
    githubRepo: string;
    contentViewableAfterSubmission: boolean;
}
export interface QuizSettingsEditorProps {
    quizProps: StaffQuizProps;
    setQuizProps: (quizProps: StaffQuizProps) => void;
}


export function QuizSettingsEditor(props: QuizSettingsEditorProps) {
    const { quizProps, setQuizProps } = props;
    const [repoUrl, setRepoUrl] = React.useState<string>('');
    return (
        <div style={{display: 'flex', flexDirection: 'column', gap: '10px'}}>
            <LabelledField label="Quiz Name" id="quizName">
                <InputText id="quizName" value={quizProps.name} onChange={(e) => setQuizProps({ ...quizProps, name: e.target.value })} />
            </LabelledField>
            <LabelledField label="Start Time" id="start-time">
                <Calendar value={quizProps.startTime} onChange={(e) => setQuizProps({ ...quizProps, startTime: e.value ?? new Date() })} showTime />
            </LabelledField>
            <LabelledField label="End Time" id="end-time">
                <Calendar value={quizProps.endTime} onChange={(e) => setQuizProps({ ...quizProps, endTime: e.value ?? new Date()})} showTime />
            </LabelledField>
            <LabelledField label="Visible At" id="vis">
                <Calendar value={quizProps.visibleAt} onChange={(e) => setQuizProps({ ...quizProps, visibleAt: e.value ?? new Date()})} showTime />
            </LabelledField>
            <LabelledField label="Release Scores At" id="vis">
                <Calendar value={quizProps.releaseTime} onChange={(e) => setQuizProps({ ...quizProps, releaseTime: e.value ?? new Date()})} showTime />
            </LabelledField>
            <LabelledField label="Github Repository URL" id="ghurl">
                <InputText id="ghurl" value={repoUrl} onChange={(e) => setRepoUrl(e.target.value)}
                    tooltip="Github repository that contains the grading scripts"/>
            </LabelledField>
            <LabelledField label="Content Viewable After Submission" id="content-viewable">
                <Checkbox id="content-viewable" checked={quizProps.contentViewableAfterSubmission} onChange={(e) => setQuizProps({ ...quizProps, contentViewableAfterSubmission: e.checked ?? false})} />
            </LabelledField>
        </div>
    );

}