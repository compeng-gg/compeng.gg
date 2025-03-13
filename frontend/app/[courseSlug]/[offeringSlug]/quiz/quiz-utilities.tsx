import { BaseQuestionData, ServerToLocal, QuestionType, CodeQuestionData, SelectQuestionData, TextQuestionData, StaffCodeQuestionData } from './question-models';


export function getQuestionDataFromRaw(rawData: any, quizSlug: string, courseSlug: string, images: string, isStaff?: boolean): any {
    const baseData: BaseQuestionData = {
        id: rawData.id,
        quizSlug: quizSlug,
        courseSlug: courseSlug,
        prompt: rawData.prompt,
        serverQuestionType: rawData.question_type,
        questionType: ServerToLocal.get(rawData.question_type) as QuestionType ?? 'TEXT',
        isMutable: true,
        totalMarks: rawData.points,
        imageUrls: JSON.parse(images.replace(/'/g, '"'))
    };
    switch (baseData.questionType) {
    case 'CODE':
        if(isStaff) {
            return {
                ...baseData,
                starterCode: rawData.starter_code, programmingLanguage: rawData.programming_language,
                filesToPull: rawData.files, fileToReplace: rawData.file_to_replace, gradingDirectory: rawData.grading_file_directory
            } as StaffCodeQuestionData;
        }
        return {
            ...baseData,
            starterCode: rawData.starter_code, programmingLanguage: rawData.programming_language
        } as CodeQuestionData;
    case 'SELECT':
        if(isStaff) {
            return {
                ...baseData,
                options: rawData.options, correctAnswerIdx: rawData.correct_option_index
            };
        }
        return {
            ...baseData,
            options: rawData.options
        } as SelectQuestionData;
    case 'TEXT':
        return {
            ...baseData,
        } as TextQuestionData;
    case 'MULTI_SELECT':
        if(isStaff) {
            return {
                ...baseData,
                options: rawData.options, correctAnswerIdxs: rawData.correct_option_indices
            };
        } else {
            return {
                ...baseData,
                options: rawData.options
            };
        }
    default:
        throw new Error(`Unsupported question type: ${JSON.stringify(rawData)}`);
    }
}
