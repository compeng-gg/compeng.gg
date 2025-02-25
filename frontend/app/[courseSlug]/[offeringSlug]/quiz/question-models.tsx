// Base Data Classes

//To-do: align question types
export const ServerToLocal = new Map([
    ["CODING", "CODE"],
    ["MULTIPLE_CHOICE", "SELECT"],
    ["WRITTEN_RESPONSE", "TEXT"]
])

export const LocalToServer = new Map([
    ["CODE", "CODING"],
    ["SELECT", "MULTIPLE_CHOICE"],
    ["TEXT", "WRITTEN_RESPONSE"]
])


export type QuestionType = "CODE" | "SELECT" | "TEXT";
export type ServerQuestionType = "CODING" | "MULTIPLE_CHOICE" | "WRITTEN_RESPONSE"

export interface BaseQuestionData {
    id: string;
    quizSlug: string;
    courseSlug: string;
    prompt: string;
    totalMarks: number;
    isMutable: boolean;
    questionType: "CODE" | "SELECT" | "TEXT";
}

export type ProgrammingLanguages = "C_PP" | "C" | "PYTHON";

// Question Data
export interface CodeQuestionData extends BaseQuestionData {
    questionType: "CODE";
    starterCode: string;
    programmingLanguage: ProgrammingLanguages;   
}

export interface StaffCodeQuestionData extends CodeQuestionData {
    filesToPull: string[];
    fileToReplace: string;
    gradingDirectory: string;
}

export interface SelectQuestionData extends BaseQuestionData {
    questionType: "SELECT";
    options: string[];
}

export interface StaffSelectQuestionData extends SelectQuestionData {
    correctAnswerIdx: number;
}

export interface TextQuestionData extends BaseQuestionData {
    questionType: "TEXT";
}

export type QuestionData = CodeQuestionData | SelectQuestionData | TextQuestionData;


export type StaffQuestionData = StaffCodeQuestionData | StaffSelectQuestionData | TextQuestionData;
// States
interface BaseState<T> {
    value: T;
    setValue: (newValue: T) => void;
}

export type CodeState = BaseState<string>; // For starterCode or similar
export type SelectState = BaseState<number>; // For selectedIdx
export type TextState = BaseState<string>; // For currentText

export type QuestionState = CodeState | SelectState | TextState;

// Utility Type to Map QuestionData to State
type QuestionTypeToStateMap = {
    CODE: CodeState;
    SELECT: SelectState;
    TEXT: TextState;
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

export type QuestionProps = (CodeQuestionProps | SelectQuestionProps | TextQuestionProps) & {viewMode : QuestionViewMode};

// Type Guards
export const isCodeQuestion = (props: QuestionProps): props is CodeQuestionProps =>
    props.questionType === "CODE";

export const isSelectQuestion = (props: QuestionProps): props is SelectQuestionProps =>
    props.questionType === "SELECT";

export const isTextQuestion = (props: QuestionProps): props is TextQuestionProps =>
    props.questionType === "TEXT";
