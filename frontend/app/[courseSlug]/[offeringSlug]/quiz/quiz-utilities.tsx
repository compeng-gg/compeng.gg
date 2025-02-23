import { BaseQuestionData, ServerToLocal, QuestionType, CodeQuestionData, SelectQuestionData, TextQuestionData } from "./question-models";


export function getQuestionDataFromRaw(rawData: any, quizSlug: string, courseSlug: string): any {
    const baseData: BaseQuestionData = {
      id: rawData.id,
      quizSlug: quizSlug,
      courseSlug: courseSlug,
      prompt: rawData.prompt,
      serverQuestionType: rawData.question_type,
      questionType: ServerToLocal.get(rawData.question_type) as QuestionType  ?? "TEXT",
      isMutable: true,
      totalMarks: rawData.points
    }
    switch (baseData.questionType) {
      case "CODE":
        return {
          ...baseData,
          starterCode: rawData.starter_code, programmingLanguage: rawData.programming_language
        } as CodeQuestionData
      case "SELECT":
        return {
          ...baseData,
          options: rawData.options
        } as SelectQuestionData
      case "TEXT":
        return {
          ...baseData,
        } as TextQuestionData
      default:
        throw new Error(`Unsupported question type: ${JSON.stringify(rawData)}`);
    }
  }