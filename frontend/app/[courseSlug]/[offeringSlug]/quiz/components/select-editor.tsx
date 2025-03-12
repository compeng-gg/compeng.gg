import { RadioButton, RadioButtonChangeEvent } from 'primereact/radiobutton';
import { SelectState } from '../question-models';

export interface SelectEditorProps {
    state: SelectState;
    options: string[];
}

export default function SelectEditor(props: SelectEditorProps){
    const {state, options} = props;

    const onChange = (e : RadioButtonChangeEvent) => {
        state.setValue(e.value);
        save(e.value);
    };
    const toDisplay = options.map((option, idx) => {
        return (
            <div key={idx} className="flex align-items-center">
                <RadioButton inputId={idx.toString()} name="questionBox" value={idx} onChange={(e) => state.setValue(e.value)} checked={state.value == idx} />
                <label className="ml-2">{options[idx]}</label>
            </div>
        );
    });

    return toDisplay;
}