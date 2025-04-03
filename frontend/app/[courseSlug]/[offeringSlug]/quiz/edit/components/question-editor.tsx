import React, { useContext, useEffect, useState } from 'react';
import { InlineMath } from 'react-katex';
import 'katex/dist/katex.min.css';
import { Card } from 'primereact/card';
import { BaseQuestionData, ID_SET_ON_SERVER, LocalToServer, ProgrammingLanguages, QuestionImage, QuestionImageStatus, QuestionProps, QuestionType, ServerQuestionType, StaffCodeQuestionData, StaffMultiSelectQuestionData, StaffQuestionData, StaffSelectQuestionData } from '../../question-models';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { MultiSelect } from 'primereact/multiselect';
import { InputNumber } from 'primereact/inputnumber';
import { Dropdown } from 'primereact/dropdown';
import { Chips } from 'primereact/chips';
import Ide from '../../components/ide';
import { ButtonGroup } from 'primereact/buttongroup';
import { Button } from 'primereact/button';
import { Checkbox } from 'primereact/checkbox';
import { QuestionImageDisplay } from '../../question-display';
import { fetchImages } from '../../quiz-utilities';
import { JwtContext } from '@/app/lib/jwt-provider';
import QuestionImageUploader from './question-image-editor';

// Error boundary for catching LaTeX rendering errors
class MathErrorBoundary extends React.Component<any, { hasError: boolean, errorMsg: string }> {
    constructor(props: any) {
        super(props);
        this.state = { hasError: false, errorMsg: '' };
    }
    static getDerivedStateFromError(error: any) {
        return { hasError: true, errorMsg: error.message };
    }
    componentDidCatch(error: any, errorInfo: any) {
        // Optionally log the error information here
    }
    render() {
        if (this.state.hasError) {
            return <div style={{ color: 'red' }}>Error in LaTeX: {this.state.errorMsg}</div>;
        }
        return this.props.children;
    }
}

export interface QuestionEditorProps {
    questionData: StaffQuestionData;
    setQuestionData: (data: StaffQuestionData | null) => void;
    moveQuestion: (delta: number) => void;
    registerDelete: (data: StaffQuestionData) => void;
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
                    <Button icon="pi pi-arrow-up" severity="secondary" tooltip="Move Up" disabled={idx === 0} onClick={() => moveQuestion(-1)}/>
                    <Button icon="pi pi-arrow-down" severity="secondary" tooltip="Move Down" disabled={idx === numQuestions - 1} onClick={() => moveQuestion(1)}/>
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
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <GenericQuestionEditor {...props} />
                <QuestionSpecificEditor {...props} />
            </div>
        </Card>
    );
}

function GenericQuestionEditor(props: QuestionEditorProps) {
    const { questionData, setQuestionData, registerDelete } = props;

    const changeQuestionType = (newType: QuestionType) => {
        console.log('Changing type from ' + questionData.questionType + ' to ' + newType);
        registerDelete(JSON.parse(JSON.stringify(questionData)));
        const tempData: BaseQuestionData = questionData as BaseQuestionData;
        tempData.questionType = newType;
        tempData.id = ID_SET_ON_SERVER;
        tempData.serverQuestionType = LocalToServer.get(newType.toString()) as ServerQuestionType;
        switch (newType) {
        case 'CODE':
            setQuestionData({ ...tempData, programmingLanguage: 'C', starterCode: '', gradingDirectory: '', filesToPull: [], fileToReplace: '' } as StaffCodeQuestionData);
            break;
        case 'TEXT':
            setQuestionData({ ...tempData } as StaffQuestionData);
            break;
        case 'SELECT':
            setQuestionData({ ...tempData, options: [], correctAnswerIdx: -1 } as StaffSelectQuestionData);
            break;
        case 'MULTI_SELECT':
            setQuestionData({ ...tempData, options: [], correctAnswerIdxs: [] } as StaffMultiSelectQuestionData);
            break;
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <TextBoxInput 
                label="Prompt" 
                value={questionData.prompt} 
                setValue={(newValue) => setQuestionData({ ...questionData, prompt: newValue })}
            />
            {/* Checkbox for toggling LaTeX rendering */}
            <BooleanInput 
                label="Render Prompt as LaTeX" 
                value={questionData.renderPromptAsLatex} 
                setValue={(newValue: boolean) => setQuestionData({ ...questionData, renderPromptAsLatex: newValue })}
            />
            {/* LaTeX Preview Box */}
            {questionData.renderPromptAsLatex && (
                <div style={{ border: '1px solid #ccc', padding: '10px', marginTop: '10px' }}>
                    <MathErrorBoundary>
                        <InlineMath math={questionData.prompt} />
                    </MathErrorBoundary>
                </div>
            )}
            <LabelledField label="Images" id="images">
                <QuestionImageUploader images={questionData.images} setImages={(images) => setQuestionData({ ...questionData, images })} courseSlug={questionData.courseSlug} quizSlug={questionData.quizSlug} />
            </LabelledField>
            <LabelledField label="Total Marks" id="marks">
                <InputNumber 
                    id="marks" 
                    value={questionData.totalMarks} 
                    showButtons 
                    onValueChange={(e) => setQuestionData({ ...questionData, totalMarks: e.value ?? 0 })}
                />
            </LabelledField>
            <LabelledField label="Question Type" id="questionType">
                <Dropdown 
                    value={questionData.questionType} 
                    options={['CODE' as QuestionType, 'TEXT' as QuestionType, 'SELECT' as QuestionType, 'MULTI_SELECT' as QuestionType]} 
                    onChange={(e) => changeQuestionType(e.value)} 
                />
            </LabelledField>
        </div>
    );
}

function TextBoxInput({ label, value, setValue }: { label: string, value: string, setValue: (newValue: string) => void }) {
    return (
        <LabelledField label={label} id={label}>
            <InputTextarea
                id={label}
                placeholder={label}
                onChange={(e) => setValue(e.target.value)}
                value={value}
                style={{ width: '100%' }}
            />
        </LabelledField>
    );
}

function BooleanInput({ label, value, setValue }: { label: string; value: boolean; setValue: (newValue: boolean) => void }) {
    return (
        <LabelledField label={label} id={label}>
            <Checkbox checked={value} onChange={(e) => setValue(e.target.checked ?? false)} />
        </LabelledField>
    );
}

// Ensures consistent label styling
export function LabelledField({ label, id, children }: { label: string, id: string, children: any }) {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', width: '100%' }}>
            <label htmlFor={id}>{label}</label>
            {children}
        </div>
    );
}

function QuestionSpecificEditor(props: QuestionEditorProps) {
    switch (props.questionData.questionType) {
    case 'CODE':
        return <CodeQuestionEditor {...props} />;
    case 'TEXT':
        return null;
    case 'SELECT':
        return <SelectQuestionEditor {...props} />;
    case 'MULTI_SELECT':
        return <MultiSelectQuestionEditor {...props} />;
    default:
        return null;
    }
}

function CodeQuestionEditor(props: QuestionEditorProps) {
    const questionData: StaffCodeQuestionData = props.questionData as StaffCodeQuestionData;
    const setQuestionData = props.setQuestionData;
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <LabelledField label="Starter Code" id="starterCode">
                <Ide 
                    value={questionData.starterCode} 
                    onChange={(newValue) => setQuestionData({ ...questionData, starterCode: newValue })} 
                    language={questionData.programmingLanguage}
                    isMutable={true}
                />
            </LabelledField>
            <LabelledField label="Programming Language" id="language">
                <Dropdown 
                    value={questionData.programmingLanguage} 
                    options={['C' as ProgrammingLanguages, 'C_PP' as ProgrammingLanguages, 'PYTHON' as ProgrammingLanguages]} 
                    onChange={(e) => setQuestionData({ ...questionData, programmingLanguage: e.value })} 
                />
            </LabelledField>
            <LabelledField label="Grading Directory" id="gradingDirectory">
                <InputText 
                    id="gradingDirectory" 
                    value={questionData.gradingDirectory} 
                    onChange={(e) => setQuestionData({ ...questionData, gradingDirectory: e.target.value })}
                    tooltip="The directory containing grade.py within the quiz repository"
                />
            </LabelledField>
            <LabelledField label="Files To Pull (Full Paths)" id="toPull">
                <Chips 
                    id="toPull" 
                    value={questionData.filesToPull} 
                    onChange={(e) => setQuestionData({ ...questionData, filesToPull: e.value ?? [] })}
                    tooltip="These files are pulled into the runner from the repository"
                />
            </LabelledField>
            <LabelledField label="File To Replace (Full Path)" id="toReplace">
                <InputText 
                    id="toReplace" 
                    value={questionData.fileToReplace} 
                    onChange={(e) => setQuestionData({ ...questionData, fileToReplace: e.target.value })}
                    tooltip="The file which will be overwritten by the students code"
                />
            </LabelledField>
        </div>
    );
}

function SelectQuestionEditor(props: QuestionEditorProps) {
    const questionData: StaffSelectQuestionData = props.questionData as StaffSelectQuestionData;
    const setQuestionData = props.setQuestionData;

    const getAnswerIdx = (answer: string) => {
        return questionData.options.indexOf(answer);
    };
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <LabelledField label="Options" id="options">
                <Chips 
                    id="options" 
                    value={questionData.options} 
                    onChange={(e) => setQuestionData({ ...questionData, options: e.value ?? [] })} 
                />
            </LabelledField>
            <LabelledField label="Correct Answer" id="answer">
                <Dropdown 
                    id="answer" 
                    value={questionData.options[questionData.correctAnswerIdx]} 
                    options={questionData.options} 
                    onChange={(e) => setQuestionData({ ...questionData, correctAnswerIdx: getAnswerIdx(e.value) })}
                />
            </LabelledField>
        </div>
    );
}

function MultiSelectQuestionEditor(props: QuestionEditorProps) {
    const questionData: StaffMultiSelectQuestionData = props.questionData as StaffMultiSelectQuestionData;
    const setQuestionData = props.setQuestionData;

    const getAnswerIdxs = (answers: string[]) => {
        return answers.map((answer) => questionData.options.indexOf(answer));
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <LabelledField label="Options" id="options">
                <Chips 
                    id="options" 
                    value={questionData.options} 
                    onChange={(e) => setQuestionData({ ...questionData, options: e.value ?? [] })}
                />
            </LabelledField>
            <LabelledField label="Correct Answers" id="answers">
                <MultiSelect 
                    id="answers" 
                    value={questionData.options.filter((_, idx) => questionData.correctAnswerIdxs.includes(idx))} 
                    options={questionData.options} 
                    onChange={(e) => setQuestionData({ ...questionData, correctAnswerIdxs: getAnswerIdxs(e.value ?? []) })}
                />
            </LabelledField>
        </div>
    );
}

