import { RadioButton, RadioButtonChangeEvent } from 'primereact/radiobutton';
import { MultiSelectQuestionProps, SelectState } from '../question-models';
import { Checkbox, CheckboxChangeEvent } from 'primereact/checkbox';

export default function MultiSelectEditor({props, save} : {props: MultiSelectQuestionProps, save: (newValue: any) => void}){
    const {state, options} = props;

    const onChange = (e : CheckboxChangeEvent) => {
        let checked = [...state.value];
        if(e.checked){
            checked.push(e.value);
        }
        else{
            checked = checked.filter((val) => val !== e.value);
        }
        state.setValue(checked);
        save(checked);
    };
    const toDisplay = options.map((option, idx) => {
        return (
            <div key={idx} className="flex align-items-center">
                <Checkbox inputId={idx.toString()} name="questionBox" value={idx} onChange={onChange} checked={state.value.includes(idx)} />
                <label className="ml-2">{options[idx]}</label>
            </div>
        );
    });

    return toDisplay;
}