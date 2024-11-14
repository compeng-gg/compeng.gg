import { Badge } from "primereact/badge";
import { Button } from "primereact/button";
import { Card } from "primereact/card";
import CodeEditor from "./code-editor";

export interface QuestionData {
    title?: string;
    text: string;
    starterCode: string;
    totalMarks: number;
    isMutable: boolean;
}

export interface QuestionProps {
    data: QuestionData
    status: QuestionStatus;
    setStatus: (newStatus: QuestionStatus) => void;
}


export interface SubmissionProps {
    submittedCode: string;
    submittedTime: Date;
    result: number;
    status: SubmissionStatus;
}

export enum SubmissionStatus {
    IN_PROGRESS = "In Progress",
    ERROR = "Error",
    SUBMITTED = "Submitted"
}

export interface QuestionStatus {
    currentText: string;
    submissions: SubmissionProps[];
    bestGrade: number; //Stored as number of marks!
}

//Display of the question inside a container
export function QuestionDisplay(props: QuestionProps){

    const {data, status, setStatus} = props;
    const {title, text, starterCode, totalMarks, isMutable} = data;

    const gradeString = `Current Grade: ${status.bestGrade}%`;

    const header = (
        <div style={{position: 'relative'}}>
            <span></span>
            <div style={{ position: 'absolute', top: '10px', right: '10px', display: 'flex', gap: '8px' }}>
                <GradeBadge grade={status.bestGrade} totalAvailable={totalMarks}/>
            </div>
        </div>
    )

    const footer = isMutable ? (
        <div style={{ position: 'relative', display: "flex", flexDirection: "row-reverse"}}>
            <span></span>
            <Button label="Submit" size="small" /> 
        </div>
    ) : null;

    const setText = (newText: string) => {
        setStatus({...status, currentText: newText})
    };

    return (
        <Card
            title={title ?? "Question"}
            subTitle={text}
            header={header}
            footer={footer}
        >
            <CodeEditor value={status.currentText} onChange={setText}/>
            <h3>Submission information here</h3>
        </Card>
    )
}

function GradeBadge({grade, totalAvailable}:{grade: number, totalAvailable: number}){
    const percentGrade = 100*(grade/totalAvailable);
    return (
        <Badge
            size="large"
            value={`Grade: ${grade}/${totalAvailable} (${percentGrade}%)`}
            severity={"success"}
        />
    );
}