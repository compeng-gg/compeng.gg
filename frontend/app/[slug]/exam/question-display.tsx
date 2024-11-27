import { Badge } from "primereact/badge";
import { Button } from "primereact/button";
import { Card } from "primereact/card";
import CodeEditor from "./components/code-editor";
import { QuestionProps } from "./question-models";
import TextEditor from "./components/text-editor";
import SelectEditor from "./components/select-editor";


//Display of the question inside a container
export function QuestionDisplay(props: QuestionProps){

    const {title, text, totalMarks, isMutable, questionType} = props;


    //To-do
    const gradeString = `Current Grade: ?%`;

    const header = (
        <div style={{position: 'relative'}}>
            <span></span>
            <div style={{ position: 'absolute', top: '10px', right: '10px', display: 'flex', gap: '8px' }}>
                <GradeBadge grade={totalMarks} totalAvailable={totalMarks}/>
            </div>
        </div>
    )

    const footer = isMutable ? (
        <div style={{ position: 'relative', display: "flex", flexDirection: "row-reverse"}}>
            <span></span>
            <Button label="Submit" size="small" /> 
        </div>
    ) : null;

    return (
        <Card
            title={title ?? "Question"}
            subTitle={text}
            header={header}
            footer={footer}
        >
            <QuestionContent {...props}/>
        </Card>
    )
}

function QuestionContent(props: QuestionProps){
    
    switch(props.questionType){
        case "CODE":
            return (
                <CodeEditor {...props.state}/>
            )
        case "TEXT":
            return (
                <TextEditor {...props.state}/>
            )
        case "SELECT":
            return (
                <SelectEditor state={props.state} options={props.options}/>
            )
    }
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