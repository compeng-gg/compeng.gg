import { Checkbox, CheckboxChangeEvent } from 'primereact/checkbox';
import { SelectState } from '../question-models';

export interface CheckboxEditorProps {
    state: SelectState;
    options: string[];
}

export default function CheckboxEditor({ props, save }: { props: CheckboxEditorProps; save: (newValue: any) => void }) {
    const { state, options } = props;

    const onChange = (e: CheckboxChangeEvent, idx: number) => {
        const updatedSelection = new Set(state.value ?? []);
        
        if (e.checked) {
            updatedSelection.add(idx);
        } else {
            updatedSelection.delete(idx);
        }

        const newValue = Array.from(updatedSelection);
        state.setValue(newValue);
        save(newValue);
    };

    return options.map((option, idx) => (
        <div key={idx} className="flex align-items-center">
            <Checkbox inputId={`checkbox-${idx}`} value={idx} onChange={(e) => onChange(e, idx)} checked={state.value?.includes(idx)} />
            <label htmlFor={`checkbox-${idx}`} className="ml-2">{option}</label>
        </div>
    ));
}
