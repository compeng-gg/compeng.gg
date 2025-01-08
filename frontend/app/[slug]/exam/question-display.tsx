import { Badge } from "primereact/badge";
import { Button } from "primereact/button";
import { Card } from "primereact/card";
import CodeEditor from "./components/code-editor";
import { isAnswered, QuestionProps } from "./question-models";
import TextEditor from "./components/text-editor";
import SelectEditor from "./components/select-editor";
import { useContext, useEffect, useRef, useState } from "react";
import { JwtContext } from "@/app/lib/jwt-provider";
import { fetchApi } from "@/app/lib/api";
import { stat } from "fs";

enum QuestionSaveStatus {
    NOT_ANSWERED = "Not Answered",
    AUTOSAVING = "Autosaving",
    TYPING = "Typing...",
    AUTOSAVED = "Autosaved",
    ERROR = "Error"
};


//Display of the question inside a container
export function QuestionDisplay(props: QuestionProps) {
    const [jwt, setAndStoreJwt] = useContext(JwtContext);

    const { title, prompt, totalMarks, isMutable, questionType, idx } = props;

    const [debouncedAnswer, setDebouncedAnswer] = useState<any>(props.state.value);

    const lastSavedRef = useRef<any>(props.state.value);

    const MS_TO_DEBOUNCE_SAVE = 5000, MS_TO_AUTO_SAVE=20*1000;

    const [status, setStatus] = useState<QuestionSaveStatus>(isAnswered(props) ? QuestionSaveStatus.AUTOSAVED : QuestionSaveStatus.NOT_ANSWERED);
    //Submits this question

    //Autosave functionality
    if(props.questionType == "TEXT" || props.questionType == "CODE"){
        useEffect(() => {
            if(props.state.value == lastSavedRef.current) return;
            if(isAnswered(props)) setStatus(QuestionSaveStatus.TYPING);
            const timer = setTimeout(() => setDebouncedAnswer(props.state.value), MS_TO_DEBOUNCE_SAVE);
            return ()=>clearTimeout(timer);
        }, [props.state.value]);

        useEffect(() => {
            if(debouncedAnswer !== lastSavedRef.current && isAnswered(props)){
                console.log("DEBOUNCE SAVING");
                save(debouncedAnswer);
            }
        }, [debouncedAnswer]);

        //Periodic save of answer. Note that this will only make an API call if the user has not stopped typing for more than debounce save ms in the last auto sav
        useEffect(() => {
            const interval = setInterval(() => {
                if (props.state.value != lastSavedRef.current && isAnswered(props)){
                    console.log("AUTOSAVING");
                    save(props.state.value);
                }
            }, MS_TO_AUTO_SAVE);
        }, [])
    }

    async function save(newValue: any) {
        try{
            setStatus(QuestionSaveStatus.AUTOSAVING);
            if(typeof newValue === "string"){
                const trimmed = newValue.trim();
                if(!trimmed.length){
                    setStatus(QuestionSaveStatus.NOT_ANSWERED);
                    return;
                }
            }
            const res = await fetchApi(jwt, setAndStoreJwt, `exams/${props.exam_slug}/answer/${props.serverQuestionType.toLowerCase()}/${props.id}/`, "POST", getAnswerBody(props, newValue));
            if(res.ok){
                lastSavedRef.current = newValue;
                setStatus(QuestionSaveStatus.AUTOSAVED);
            } else {
                setStatus(QuestionSaveStatus.ERROR);
            } 
        } catch (error){
            console.log("Error submitting question", error);
            setStatus(QuestionSaveStatus.ERROR);
        }
    }


    //To-do
    const gradeString = `Current Grade: ?%`;

    const header = (
        <div style={{ position: 'relative' }}>
            <span></span>
            <div style={{ position: 'absolute', top: '10px', right: '10px', display: 'flex', gap: '8px' }}>
                <StatusBadge status={status}/>
                <GradeBadge grade={undefined} totalAvailable={totalMarks} />
            </div>
        </div>
    )

    // const footer = isMutable ? (
    //     <div style={{ position: 'relative', display: "flex", flexDirection: "row-reverse"}}>
    //         <span></span>
    //         <Button label="Submit" size="small" onClick={() => submit()}/> 
    //     </div>
    // ) : null;

    return (
        <Card
            title={title ?? `Question ${idx != undefined ? idx+1:''}`}
            subTitle={prompt}
            header={header}
        >
            <QuestionContent props={props} save={save}/>
        </Card>
    )
}



function QuestionContent({props, save} : {props: QuestionProps, save: (newValue: any) => void}) {

    switch (props.questionType) {
        case "CODE":
            return (
                <CodeEditor props={props} save={save} />
            )
        case "TEXT":
            return (
                <TextEditor state={props.state} save={save} />
            )
        case "SELECT":
            return (
                <SelectEditor props={props} save={save} />
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

function StatusToSeverity(status: QuestionSaveStatus){
    switch(status){
        case QuestionSaveStatus.AUTOSAVED:
            return "success";
        case QuestionSaveStatus.ERROR:
            return "danger";
        case QuestionSaveStatus.NOT_ANSWERED:
            return "secondary";
        default:
            return "info";
    }
}

function StatusBadge({status} : {status : QuestionSaveStatus}) {

    return (
        <Badge
            size="large"
            value={status}
            severity={StatusToSeverity(status)}
        />
    )
}


function getAnswerBody(props: QuestionProps, value: any) {
    switch (props.questionType) {
        case "CODE":
            return { solution: value };
        case "SELECT":
            return { selected_answer_index: value };
        case "TEXT":
            return { response: value};
    }
}