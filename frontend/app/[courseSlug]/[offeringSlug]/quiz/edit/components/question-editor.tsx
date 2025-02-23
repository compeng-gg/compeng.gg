import { Card } from "primereact/card";
import { QuestionData, QuestionType } from "../../question-models";
import { InputText } from "primereact/inputtext";
import { InputTextarea } from "primereact/inputtextarea";
import { KeyFilterType } from "primereact/keyfilter";
import { InputNumber } from "primereact/inputnumber";
import { ListBox } from "primereact/listbox";
import { MultiSelect } from "primereact/multiselect";
import { Dropdown } from "primereact/dropdown";

export interface QuestionEditorProps {
    questionData: QuestionData;
    setQuestionData: (data: QuestionData) => void;
    idx: number;
}

export default function QuestionEditor(props: QuestionEditorProps) {
    
    const { questionData, setQuestionData, idx } = props;
    return (
        <Card
            title={questionData.title ?? `Question ${idx !== undefined ? idx + 1 : ''}`}
        >   
            <GenericQuestionEditor {...props}/>
            {/* <QuestionSpecificEditor {...props}/> */}
        </Card>
    )
}

function GenericQuestionEditor (props: QuestionEditorProps) {

   const {questionData, setQuestionData, idx} = props;

   return (
        <div style={{display: "flex", flexDirection: "column", gap: "10px"}}>
            <TextInput label="Grading Directory" value={questionData.title ?? ''} setValue={(newValue) => setQuestionData({ ...questionData, title: newValue })} />
            <TextBoxInput label="Prompt" value={questionData.prompt} setValue={(newValue) => setQuestionData({ ...questionData, prompt: newValue })} />
            <LabelledField label="Total Marks" id="marks">
                <InputNumber id="marks" value={questionData.totalMarks} showButtons onValueChange={(e) => setQuestionData({ ...questionData, totalMarks: e.value ?? 0 })} />
            </LabelledField>
            <LabelledField label="Question Type" id="questionType">
                <Dropdown value={questionData.questionType} options={["CODE" as QuestionType, "TEXT" as QuestionType, "SELECT" as QuestionType]} onChange={(e) => setQuestionData({ ...questionData, questionType: e.value})} />
            </LabelledField>
        </div>
   )


}

function TextInput({ label, value, setValue }: { label: string, value: string, setValue: (newValue: string) => void}) {
    return (
        <LabelledField label={label} id={label}>
            <InputText
                id={label}
                placeholder={label}
                onChange={(e) => setValue(e.target.value)}
                value={value}
                style={{width: "50%"}}
            />
        </LabelledField>
    );
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
function LabelledField({label, id, children}: {label: string, id: string, children: any}) {
    return (
        <div style={{display: "flex", flexDirection: "column", gap: "5px"}}>
            <label htmlFor={id}>{label}</label>
            {children}
        </div>
    )
}

function QuestionSpecificEditor(props: QuestionEditorProps) {
    switch (props.questionData.questionType) {
        case "CODE":
            return <CodeQuestionEditor {...props}/>;
        case "TEXT":
            return <TextQuestionEditor questionData={questionData} setQuestionData={setQuestionData} />;
        case "SELECT":
            return <SelectQuestionEditor questionData={questionData} setQuestionData={setQuestionData} />;
        default:
            return null;
    }
}

function CodeQuestionEditor(props: QuestionEditorProps) {
    const { questionData, setQuestionData} = props;
    
    return (
        <div style={{display: "flex", flexDirection: "column", gap: "10px"}}>
            <TextBoxInput label="Starter Code" value={questionData.starterCode} setValue={(newValue) => setQuestionData({ ...questionData, starterCode: newValue })} />
            <LabelledField label="Programming Language" id="language">
                <Dropdown value={questionData.programmingLanguage} options={["C" as ProgrammingLanguages, "C_PP" as ProgrammingLanguages, "PYTHON" as ProgrammingLanguages]} onChange={(e) => setQuestionData({ ...questionData, programmingLanguage: e.value })} />
            </LabelledField>
        </div>
    )
}