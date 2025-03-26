// Base Data Classes

//To-do: align question types
export const ServerToLocal = new Map([
    ['CODING', 'CODE'],
    ['MULTIPLE_CHOICE', 'SELECT'],
    ['WRITTEN_RESPONSE', 'TEXT'],
    ['CHECKBOX', 'MULTI_SELECT']
]);

export const LocalToServer = new Map([
    ['CODE', 'CODING'],
    ['SELECT', 'MULTIPLE_CHOICE'],
    ['TEXT', 'WRITTEN_RESPONSE'],
    ['MULTI_SELECT', 'CHECKBOX']
]);

export const ID_SET_ON_SERVER = 'set_on_server';

export type QuestionType = 'CODE' | 'SELECT' | 'TEXT' | 'MULTI_SELECT';
export type ServerQuestionType = 'CODING' | 'MULTIPLE_CHOICE' | 'WRITTEN_RESPONSE' | 'CHECKBOX';

export type QuestionImageStatus = "IMMUTABLE" | "NEW" | "DELETED" | "MODIFIED" | "UNMODIFIED" | "FRESH_LOAD";


export interface QuestionImage {
    id: string;
    caption: string;
    status: QuestionImageStatus; 
    order: number;
    file?: File;
}



export interface BaseQuestionData {
    id: string;
    quizSlug: string;
    courseSlug: string;
    prompt: string;
    totalMarks: number;
    isMutable: boolean;
    questionType: QuestionType;
    serverQuestionType: ServerQuestionType;
    images: QuestionImage[];
    imageStatus?: QuestionImageStatus[]; 
    idx?: number;
    renderPromptAsLatex: boolean;
}

export type ProgrammingLanguages = 'C_PP' | 'C' | 'PYTHON';

// Question Data
export interface CodeQuestionData extends BaseQuestionData {
    questionType: 'CODE';
    starterCode: string;
    programmingLanguage: ProgrammingLanguages;   
}

export interface StaffCodeQuestionData extends CodeQuestionData {
    filesToPull: string[];
    fileToReplace: string;
    gradingDirectory: string;
}

export interface SelectQuestionData extends BaseQuestionData {
    questionType: 'SELECT';
    options: string[];
}

export interface StaffSelectQuestionData extends SelectQuestionData {
    correctAnswerIdx: number;
}

export interface MultiSelectQuestionData extends BaseQuestionData {
    questionType: 'MULTI_SELECT';
    options: string[];
}

export interface StaffMultiSelectQuestionData extends MultiSelectQuestionData {
    correctAnswerIdxs: number[];
}

export interface TextQuestionData extends BaseQuestionData {
    questionType: 'TEXT';
}

export type QuestionData = CodeQuestionData | SelectQuestionData | TextQuestionData | MultiSelectQuestionData;


export type StaffQuestionData = StaffCodeQuestionData | StaffSelectQuestionData | TextQuestionData | StaffMultiSelectQuestionData;
// States
interface BaseState<T> {
    value: T;
    setValue: (newValue: T) => void;
}

export type CodeState = BaseState<string>; // For starterCode or similar
export type SelectState = BaseState<number>; // For selectedIdx
export type TextState = BaseState<string>; // For currentText
export type MultiSelectState = BaseState<number[]>; // For selectedIdxs

export type QuestionState = CodeState | SelectState | TextState;

// Utility Type to Map QuestionData to State
type QuestionTypeToStateMap = {
    CODE: CodeState;
    SELECT: SelectState;
    TEXT: TextState;
    MULTI_SELECT: MultiSelectState;
};

//An enum with the below values
export enum QuestionViewMode {
    STUDENT_WRITE,
    STUDENT_VIEW,
    INSTRUCTOR_EDIT,
    INSTRUCTOR_GRADE
};
// Final Question Props
export type CodeQuestionProps = CodeQuestionData & { state: CodeState };
export type SelectQuestionProps = SelectQuestionData & { state: SelectState };
export type TextQuestionProps = TextQuestionData & { state: TextState };
export type MultiSelectQuestionProps = MultiSelectQuestionData & { state: MultiSelectState };

export type QuestionProps = (CodeQuestionProps | SelectQuestionProps | TextQuestionProps | MultiSelectQuestionProps)

// Type Guards
export const isCodeQuestion = (props: QuestionProps): props is CodeQuestionProps =>
    props.questionType === 'CODE';

export const isSelectQuestion = (props: QuestionProps): props is SelectQuestionProps =>
    props.questionType === 'SELECT';

export const isTextQuestion = (props: QuestionProps): props is TextQuestionProps =>
    props.questionType === 'TEXT';

export const isMultiSelectQuestion = (props: QuestionProps): props is MultiSelectQuestionProps =>
    props.questionType === 'MULTI_SELECT';

export const isAnswered = (props: QuestionProps) => {
    switch(props.questionType){
    case 'TEXT':
        return props.state.value.length;
    case 'CODE':
        return props.state.value != props.starterCode;
    case 'SELECT':
        return props.state.value != -1;
    case 'MULTI_SELECT':
        return props.state.value.length;
    }
};
