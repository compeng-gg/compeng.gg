import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';
import { useContext } from 'react';
import { BaseQuestionData, ServerToLocal, QuestionType, CodeQuestionData, SelectQuestionData, TextQuestionData, StaffCodeQuestionData, QuestionImage } from './question-models';


export function getQuestionDataFromRaw(rawData: any, quizSlug: string, courseSlug: string, isStaff?: boolean): any {
    const baseData: BaseQuestionData = {
        id: rawData.id,
        quizSlug: quizSlug,
        courseSlug: courseSlug,
        prompt: rawData.prompt,
        serverQuestionType: rawData.question_type,
        questionType: ServerToLocal.get(rawData.question_type) as QuestionType ?? 'TEXT',
        isMutable: true,
        images: getImagesFromRaw(rawData.images, isStaff).sort((a, b) => a.order - b.order),
        totalMarks: rawData.points,
        renderPromptAsLatex: rawData.render_prompt_as_latex
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

function getImagesFromRaw(rawImages: any[], isStaff?: boolean): QuestionImage[] {
    return rawImages.map((image) => {
        return {
            id: image.id,
            caption: image.caption,
            status: isStaff ? 'UNMODIFIED' : 'IMMUTABLE',
            order: image.order
        };
    })
}

export async function fetchImagesAsFiles(images: QuestionImage[], courseSlug: string, quizSlug: string, jwt: string, setAndStoreJwt: (jwt: string) => void) {

    try {
        const files = await Promise.all(
            images.map(async (image, index) => {
                const res = await fetchApi(
                    jwt,
                    setAndStoreJwt,
                    `quizzes/${courseSlug}/${quizSlug}/image/${image.id}`,
                    'GET',
                );
                const blob = await res.blob();
                return new File([blob], image.caption ?? `image-${index + 1}.png`, {
                type: blob.type || 'image/png',
                });
            })
        );

        return files;
    } catch (error) {
        console.error('Error fetching images:', error);
    }
}

export async function fetchImages(images: QuestionImage[], courseSlug: string, quizSlug: string, jwt: string, setAndStoreJwt: (jwt: string) => void, returnAsFile?: boolean) {

        try {
            const srcs = await Promise.all(
                images.map(async (image, index) => {
                    const res = await fetchApi(
                        jwt,
                        setAndStoreJwt,
                        `quizzes/${courseSlug}/${quizSlug}/image/${image.id}`,
                        'GET',
                    );
                    const buffer = await res.arrayBuffer();
                    const base64String = btoa(
                        new Uint8Array(buffer).reduce((data, byte) => data + String.fromCharCode(byte), '')
                    );

                    return `data:image/png;base64,${base64String}`;
                })
            );

            return srcs;
        } catch (error) {
            console.error('Error fetching images:', error);
        }
    }
