import { RadioButton, RadioButtonChangeEvent } from 'primereact/radiobutton';
import { SelectState } from '../question-models';

export interface SelectEditorProps {
    state: SelectState;
    options: string[];
}

export default function SelectEditor({props, save} : {props: SelectEditorProps, save: (newValue: any) => void}){
    const {state, options} = props;

    const onChange = (e : RadioButtonChangeEvent) => {
        state.setValue(e.value);
        save(e.value);
    };
    const toDisplay = options.map((option, idx) => {
        return (
            <div key={idx} className="flex align-items-center">
                <RadioButton inputId={idx.toString()} name="questionBox" value={idx} onChange={onChange} checked={state.value == idx} />
                <label className="ml-2">{options[idx]}</label>
            </div>
        );
    });

    return toDisplay;
}