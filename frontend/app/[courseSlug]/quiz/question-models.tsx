// Base Data Classes
interface BaseQuestionData {
    title?: string;
    id: string;
    quizSlug: string;
    courseSlug: string;
    prompt: string;
    totalMarks: number;
    isMutable: boolean;
    questionType: "CODE" | "SELECT" | "TEXT";
}

// Question Data
export interface CodeQuestionData extends BaseQuestionData {
    questionType: "CODE";
    starterCode: string;
}

export interface SelectQuestionData extends BaseQuestionData {
    questionType: "SELECT";
    options: string[];
}

export interface TextQuestionData extends BaseQuestionData {
    questionType: "TEXT";
}

export type QuestionData = CodeQuestionData | SelectQuestionData | TextQuestionData;

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

// Final Question Props
export type CodeQuestionProps = CodeQuestionData & { state: CodeState };
export type SelectQuestionProps = SelectQuestionData & { state: SelectState };
export type TextQuestionProps = TextQuestionData & { state: TextState };

export type QuestionProps = CodeQuestionProps | SelectQuestionProps | TextQuestionProps;

// Type Guards
export const isCodeQuestion = (props: QuestionProps): props is CodeQuestionProps =>
    props.questionType === "CODE";

export const isSelectQuestion = (props: QuestionProps): props is SelectQuestionProps =>
    props.questionType === "SELECT";

export const isTextQuestion = (props: QuestionProps): props is TextQuestionProps =>
    props.questionType === "TEXT";
