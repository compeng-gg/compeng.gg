import { Badge } from "primereact/badge";
import { Button } from "primereact/button";
import { Card } from "primereact/card";
import CodeEditor from "./components/code-editor";
import { QuestionProps } from "./question-models";
import TextEditor from "./components/text-editor";
import SelectEditor from "./components/select-editor";
import { useContext } from "react";
import { JwtContext } from "@/app/lib/jwt-provider";
import { fetchApi } from "@/app/lib/api";


//Display of the question inside a container
export function QuestionDisplay(props: QuestionProps) {
    const [jwt, setAndStoreJwt] = useContext(JwtContext);

    const { title, prompt, totalMarks, isMutable, questionType, idx } = props;

    //Submits this question


    async function submit() {
        const res = await fetchApi(jwt, setAndStoreJwt, `assessments/${props.assessment_slug}/answer/${props.serverQuestionType.toLowerCase()}/${props.id}/`, "POST", getAnswerBody(props));
        const data = await res.json();

        console.log("SUBMITTED. result:\n", JSON.stringify(data, null, 2));
    }



    //To-do
    const gradeString = `Current Grade: ?%`;

    const header = (
        <div style={{ position: 'relative' }}>
            <span></span>
            <div style={{ position: 'absolute', top: '10px', right: '10px', display: 'flex', gap: '8px' }}>
                <GradeBadge grade={undefined} totalAvailable={totalMarks} />
            </div>
        </div>
    )

    const footer = isMutable ? (
        <div style={{ position: 'relative', display: "flex", flexDirection: "row-reverse"}}>
            <span></span>
            <Button label="Submit" size="small" onClick={() => submit()}/> 
        </div>
    ) : null;

    return (
        <Card
            title={title ?? `Question ${idx ? idx+1:''}`}
            subTitle={prompt}
            header={header}
            footer={footer}
        >
            <QuestionContent {...props} />
        </Card>
    )
}

function QuestionContent(props: QuestionProps) {

    switch (props.questionType) {
        case "CODE":
            return (
                <CodeEditor {...props} />
            )
        case "TEXT":
            return (
                <TextEditor {...props.state} />
            )
        case "SELECT":
            return (
                <SelectEditor state={props.state} options={props.options} />
            )
    }
}

function GradeBadge({ grade, totalAvailable }: { grade?: number, totalAvailable: number }) {
    const percentGrade = 100 * (grade ?? 0 / totalAvailable);
    const value: string = (grade) ? `Grade: ${grade}/${totalAvailable} (${percentGrade}%)` : `Points: ${totalAvailable}`
    const severity = (grade) ? "success" : "info";
    return (
        <Badge
            size="large"
            value={value}
            severity={severity}
        />
    );
}


function getAnswerBody(props: QuestionProps) {
    switch (props.questionType) {
        case "CODE":
            return { solution: props.state.value };
        case "SELECT":
            return { selected_answer_index: props.state.value };
        case "TEXT":
            return { response: props.state.value };
    }
}