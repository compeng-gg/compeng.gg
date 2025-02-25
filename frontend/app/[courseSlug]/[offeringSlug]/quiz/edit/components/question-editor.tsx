import { Card } from "primereact/card";
import { BaseQuestionData, LocalToServer, ProgrammingLanguages, QuestionData, QuestionType, ServerQuestionType, ServerToLocal, StaffCodeQuestionData, StaffQuestionData, StaffSelectQuestionData } from "../../question-models";
import { InputText } from "primereact/inputtext";
import { InputTextarea } from "primereact/inputtextarea";
import { KeyFilterType } from "primereact/keyfilter";
import { InputNumber } from "primereact/inputnumber";
import { ListBox } from "primereact/listbox";
import { MultiSelect } from "primereact/multiselect";
import { Dropdown } from "primereact/dropdown";
import { Chips } from "primereact/chips";
import { FloatLabel } from "primereact/floatlabel";
import Ide from "../../components/ide";
import { ButtonGroup } from "primereact/buttongroup";
import { Button } from "primereact/button";

export interface QuestionEditorProps {
    questionData: StaffQuestionData;
    setQuestionData: (data: StaffQuestionData | null) => void;
    moveQuestion: (delta: number) => void;
    idx: number;
    numQuestions: number;

}

export default function QuestionEditor(props: QuestionEditorProps) {
    
    const { questionData, setQuestionData, moveQuestion, numQuestions, idx } = props;

    const header = (
        <div style={{ position: 'relative' }}>
            <span></span>
            <div style={{ position: 'absolute', top: '10px', right: '10px', display: 'flex', gap: '8px' }}>
                <ButtonGroup>
                    <Button icon="pi pi-arrow-up" severity="secondary" tooltip="Move Up" disabled={idx == 0} onClick={() => moveQuestion(-1)}/>
                    <Button icon="pi pi-arrow-down" severity="secondary" tooltip="Move Down" disabled={idx == numQuestions-1} onClick={() => moveQuestion(1)}/>
                </ButtonGroup>
                <Button icon="pi pi-trash" severity="danger" onClick={() => setQuestionData(null)}/>
            </div>
        </div>
    );
    return (
        <Card
            title={`Question ${idx !== undefined ? idx + 1 : ''}`}
            key={idx}
            header={header}
        >   
            <div style={{display: "flex", flexDirection: "column", gap: "10px"}}>
                <GenericQuestionEditor {...props}/>
                <QuestionSpecificEditor {...props}/>
            </div>
        </Card>
    )
}

function GenericQuestionEditor (props: QuestionEditorProps) {

   const {questionData, setQuestionData, idx} = props;

   const changeQuestionType = (newType: QuestionType) => {
        //Convert old data to generic
        const tempData: BaseQuestionData = questionData as BaseQuestionData;
        tempData.questionType = newType;
        console.log(newType);
        tempData.serverQuestionType = LocalToServer.get(newType.toString()) as ServerQuestionType;
        console.log(tempData);
        switch(newType) {
            case "CODE":
                setQuestionData({...tempData, programmingLanguage: "C", starterCode: "", gradingDirectory: "", filesToPull: [], fileToReplace: ""} as StaffCodeQuestionData);
                break;
            case "TEXT":
                setQuestionData({...tempData} as StaffQuestionData);
                break;
            case "SELECT":
                setQuestionData({...tempData, options: [], correctAnswerIdx: -1} as StaffSelectQuestionData);
                break;
        }       
    }

   return (
        <div style={{display: "flex", flexDirection: "column", gap: "10px"}}>
            <TextBoxInput label="Prompt" value={questionData.prompt} setValue={(newValue) => setQuestionData({ ...questionData, prompt: newValue })} />
            <LabelledField label="Total Marks" id="marks">
                <InputNumber id="marks" value={questionData.totalMarks} showButtons onValueChange={(e) => setQuestionData({ ...questionData, totalMarks: e.value ?? 0 })} />
            </LabelledField>
            <LabelledField label="Question Type" id="questionType">
                <Dropdown value={questionData.questionType} options={["CODE" as QuestionType, "TEXT" as QuestionType, "SELECT" as QuestionType]} onChange={(e) => changeQuestionType(e.value)} />
            </LabelledField>
        </div>
   )


}

function TextBoxInput({label, value, setValue}: {label: string, value: string, setValue: (newValue: string) => void}) {
    return (
        <LabelledField label={label} id={label}>
            <InputTextarea
                id={label}
                placeholder={label}
                onChange={(e) => setValue(e.target.value)}
                value={value}
                style={{width: "100%"}}
            />
        </LabelledField>
    );
}

//Ensures consistent label styling
export function LabelledField({label, id, children}: {label: string, id: string, children: any}) {
    return (
        <div style={{display: "flex", flexDirection: "column", gap: "5px", width: "100%"}}>
            <label htmlFor={id}>{label}</label>
            {children}
        </div>
    )
}

function QuestionSpecificEditor(props: QuestionEditorProps) {
    switch (props.questionData.questionType) {
        case "CODE":
            return <CodeQuestionEditor {...props}/>;
        case "TEXT": //No specific fields
            return null;
        case "SELECT":
            return <SelectQuestionEditor {...props} />;
        default:
            return null;
    }
}

function CodeQuestionEditor(props: QuestionEditorProps) {
    const questionData : StaffCodeQuestionData = props.questionData as StaffCodeQuestionData;
    const setQuestionData = props.setQuestionData;
    return (
        <div style={{display: "flex", flexDirection: "column", gap: "10px"}}>
            <LabelledField label="Starter Code" id="starterCode">
                <Ide value={questionData.starterCode} onChange={(newValue) => setQuestionData({ ...questionData, starterCode: newValue })} language={questionData.programmingLanguage}/>
            </LabelledField>
            <LabelledField label="Programming Language" id="language">
                <Dropdown value={questionData.programmingLanguage} options={["C" as ProgrammingLanguages, "C_PP" as ProgrammingLanguages, "PYTHON" as ProgrammingLanguages]} onChange={(e) => setQuestionData({ ...questionData, programmingLanguage: e.value })} />
            </LabelledField>
            <LabelledField label="Grading Directory" id="gradingDirectory">
                <InputText id="gradingDirectory" value={questionData.gradingDirectory} onChange={(e) => setQuestionData({ ...questionData, gradingDirectory: e.target.value })}
                    tooltip="The directory containing grade.py within the quiz repository"/>
            </LabelledField>
            <LabelledField label="Files To Pull (Full Paths)" id="toPull">
                <Chips id="toPull" value={questionData.filesToPull} onChange={(e) => setQuestionData({ ...questionData, filesToPull: e.value ?? [] })}
                    tooltip="These files are pulled into the runner from the repository"/>
            </LabelledField>
            <LabelledField label="File To Replace (Full Path)" id="toReplace">
                <InputText id="toReplace" value={questionData.fileToReplace} onChange={(e) => setQuestionData({ ...questionData, fileToReplace: e.target.value })}
                tooltip="The file which will be overwritten by the students code"/>
            </LabelledField>
        </div>
    )
}

function SelectQuestionEditor(props: QuestionEditorProps) {
    const questionData : StaffSelectQuestionData = props.questionData as StaffSelectQuestionData;
    const setQuestionData = props.setQuestionData;

    const getAnswerIdx = (answer: string) => {
        return questionData.options.indexOf(answer);
    }
    return (
        <div style={{display: "flex", flexDirection: "column", gap: "10px"}}>
            <LabelledField label="Options" id="options">
                <Chips id="options" value={questionData.options} onChange={(e) => setQuestionData({ ...questionData, options: e.value ?? [] })} />
            </LabelledField>
            <LabelledField label="Correct Answer" id="answer">
                <Dropdown id="answer" value={questionData.options[questionData.correctAnswerIdx]} options={questionData.options} onChange={(e) => setQuestionData({ ...questionData, correctAnswerIdx: getAnswerIdx(e.value)})} />
            </LabelledField>
        </div>
    )
}