import { InputTextarea } from "primereact/inputtextarea";
import { TextState } from "../question-models";

export default function TextEditor(state: TextState){

    return (
        <InputTextarea autoResize value={state.value} onChange={(e) => state.setValue(e.target.value)} style={{width: "100%"}}/> 
    )
}