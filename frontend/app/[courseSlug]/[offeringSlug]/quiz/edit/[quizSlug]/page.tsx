'use client';

import { useContext, useEffect, useState } from 'react';
import { ID_SET_ON_SERVER, QuestionData, QuestionImage, StaffQuestionData } from '../../question-models';
import { QuizProps } from '../../quiz-display';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';
import { getQuestionDataFromRaw } from '../../quiz-utilities';
import { id, se } from 'date-fns/locale';
import Navbar from '@/app/ui/navbar';
import LoginRequired from '@/app/lib/login-required';
import QuestionEditor from '../components/question-editor';
import { QuizSettingsEditor } from '../components/quiz-settings-editor';
import { Button } from 'primereact/button';

export interface StaffQuizProps {
    name: string;
    courseSlug: string;
    quizSlug: string;
    startTime: Date;
    endTime: Date;
    visibleAt: Date;
    releaseTime: Date;
    githubRepo: string;
    contentViewableAfterSubmission: boolean;
}


export default function Page({ params }: { params: { courseSlug: string, quizSlug: string } }) {

    const { courseSlug, quizSlug } = params;
    const [jwt, setAndStoreJwt] = useContext(JwtContext);
    const [quiz, setQuiz] = useState<StaffQuizProps | undefined>(undefined);
    const [questionData, setQuestionData] = useState<StaffQuestionData[]>([]);
    const [deletedQuestions, setDeletedQuestions] = useState<StaffQuestionData[]>([]);
    const [loaded, setLoaded] = useState<boolean>(false);
    const [modified, setModified] = useState<boolean>(false);
    
    async function fetchQuiz() {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `quizzes/admin/${courseSlug}/${quizSlug}/`, 'GET');
            const data = await res.json();
            const retQuiz: StaffQuizProps = {
                startTime: new Date(data.starts_at * 1000),
                endTime: new Date(data.ends_at * 1000),
                visibleAt: new Date(data.visible_at * 1000),
                releaseTime: new Date(data.release_at * 1000),
                quizSlug: quizSlug,
                name: data.title,
                courseSlug: courseSlug,
                githubRepo: data.github_repository,
                contentViewableAfterSubmission: data.content_viewable_after_submission
            };
            setQuiz(retQuiz);
            console.log('Quiz' + JSON.stringify(data, null, 2));
            setQuestionData((data.questions.map((rawData: any) => getQuestionDataFromRaw(rawData, quizSlug, courseSlug, true))));
        } catch (error) {
            console.error('Failed to retrieve quiz', error);
        }
    }

    const addQuestion= () => {
        setModified(true);
        const newQuestion = {
            id: ID_SET_ON_SERVER,
            quizSlug: quizSlug,
            courseSlug: courseSlug,
            prompt: '',
            totalMarks: 0,
            isMutable: true,
            questionType: 'TEXT',
            renderPromptAsLatex: false,
            serverQuestionType: 'WRITTEN_RESPONSE'
        } as StaffQuestionData;
        setQuestionData(prevData => [...prevData, newQuestion]);
    };

    const move = (idx: number, delta: number) => {
        console.log('Moving question', idx, delta);
        const temp = JSON.parse(JSON.stringify(questionData));
        temp[idx] = questionData[idx+delta];
        temp[idx+delta] = questionData[idx];
        setQuestionData(temp);
    };

    const registerDelete = (questionData: StaffQuestionData) => {
        console.log('Registering delete', questionData);
        setDeletedQuestions(prevData => [...prevData, questionData]);
    };

    useEffect(() => {
        if (!loaded) {
            fetchQuiz();
            setLoaded(true);
        }
    }, [loaded]);

    const setQuestionDataAtIdx = (idx: number, data: StaffQuestionData | null) => {
        setModified(true);
        if(data === null) {
            //Add to deletion
            registerDelete(questionData[idx]);
            setQuestionData(prevData => {
                const newData = [...prevData];
                newData.splice(idx, 1);
                return newData;
            });
            return;
        }
        setQuestionData(prevData => {
            const newData = [...prevData];
            newData[idx] = data;
            return newData;
        });
    };

    const setQuizPropsCustom = (newProps: StaffQuizProps) => {
        setModified(true);
        setQuiz(newProps);
    };

    if (!loaded) {
        return (
            <LoginRequired>
                <Navbar />

                <h3 style={{ color: 'yellow' }}>{`Loading quiz ${quizSlug}...`}</h3>
            </LoginRequired>
        );
    }

    if (!quiz) {
        return (
            <LoginRequired>
                <Navbar />

                <h3 style={{ color: 'yellow' }}>{`quiz ${quizSlug} not found for course ${courseSlug}`}</h3>
            </LoginRequired>
        );
    }
    return (
        <LoginRequired>
            <Navbar />
            <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-16">
                <QuizEditorTopbar quiz={quiz} fetchQuiz={fetchQuiz} deletedQuestions={deletedQuestions} setDeletedQuestions={setDeletedQuestions} questionData={questionData} modified={modified} setModified={setModified} />
                <div style={{ display: 'flex', gap: '10px', width: '100%', flexDirection: 'column' }}>
                    <QuizSettingsEditor quizProps={quiz} setQuizProps={(newProps) => setQuizPropsCustom(newProps)} />
                    {questionData.map((data, idx) => (
                        <QuestionEditor
                            key={data.id || idx} // Use a unique id if available; otherwise, fallback to the index
                            questionData={data}
                            setQuestionData={(newData) => setQuestionDataAtIdx(idx, newData)}
                            idx={idx}
                            numQuestions={questionData.length}
                            moveQuestion={(delta: number) => move(idx, delta)}
                            registerDelete={registerDelete}
                        />
                    ))}
                    <AddQuestionButton addQuestion={addQuestion}/>
                </div> 
            </div>
        </LoginRequired>
    );
}

interface QuizEditorTopbarProps {
    quiz: StaffQuizProps;
    questionData: StaffQuestionData[];
    modified: boolean;
    deletedQuestions: StaffQuestionData[];
    fetchQuiz: () => void;
    setDeletedQuestions: (newVal: StaffQuestionData[]) => void;
    setModified: (newVal: boolean) => void;
}

function QuizEditorTopbar(props: QuizEditorTopbarProps) {
    const { quiz, questionData, modified, setModified, deletedQuestions, setDeletedQuestions } = props;

    const [error, setError] = useState<boolean>(false);

    const undoChanges = () => {
        props.fetchQuiz();
        setModified(false);
    };
    const [jwt, setAndStoreJwt] = useContext(JwtContext);

    async function createQuestion(questionData: StaffQuestionData, idx: number) {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `quizzes/admin/${quiz.courseSlug}/${quiz.quizSlug}/${questionData.serverQuestionType.toLowerCase()}/create/`, 'POST', serializeQuestionData(questionData, idx));
            if(!res.ok){
                console.error('Failed to create question', JSON.stringify(questionData, null, 2), res);
                throw new Error('Failed to create question');
            }
        } catch(e) {
            setError(true);
            console.error('Failed to create question', JSON.stringify(questionData, null, 2), e);
        }
    }

    async function saveQuestion(questionData: StaffQuestionData, idx: number) {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `quizzes/admin/${quiz.courseSlug}/${quiz.quizSlug}/${questionData.serverQuestionType.toLowerCase()}/${questionData.id}/edit/`, 'POST', serializeQuestionData(questionData, idx));
            if(!res.ok){
                throw new Error('Failed to save question');
            }
        }
        catch(e) {
            setError(true);
            console.error('Failed to save question', JSON.stringify(questionData, null, 2), e);
        }
    }


    async function deleteQuestion(questionData: StaffQuestionData) {
        if(questionData.id === ID_SET_ON_SERVER) return;
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `quizzes/admin/${quiz.courseSlug}/${quiz.quizSlug}/${questionData.serverQuestionType.toLowerCase()}/${questionData.id}/delete/`, 'DELETE');
            if(!res.ok){
                throw new Error('Failed to delete question');
            }
        } 
        catch(e) {
            setError(true);
            console.error('Failed to delete question', JSON.stringify(questionData, null, 2), e);
        }
    }

    async function updateQuiz() {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `quizzes/admin/${quiz.courseSlug}/${quiz.quizSlug}/edit/`, 'POST', serializeQuizData(quiz));
            if(!res.ok){
                throw new Error('Failed to save question');
            }
        } catch(e) {
            setError(true);
            console.error('Failed to update quiz', JSON.stringify(quiz, null, 2), e);
        }

    }

    async function saveQuestionImages(questionData: StaffQuestionData, idx: number) {
        console.log('Saving question images:');
        console.log(JSON.stringify(questionData.images, null, 2));
        try {
            questionData.images.map(async (image, imageIdx) => {
                var res;
                if(image.status == 'UNMODIFIED'){
                    return;
                }
                if(image.status == 'NEW'){
                    //creation flow
                    res = await fetchApi(jwt, setAndStoreJwt, `quizzes/admin/${quiz.courseSlug}/${quiz.quizSlug}/images/add/`, 'POST',
                        createImageBody(image, questionData, imageIdx) ?? {}
                    );
                } else if (image.status == 'DELETED'){
                    //deletion flow
                    res = await fetchApi(jwt, setAndStoreJwt, `quizzes/admin/${quiz.courseSlug}/${quiz.quizSlug}/images/delete/${image.id}/`, 'DELETE');
                } else if (image.status == 'MODIFIED'){
                    //update flow
                    res = await fetchApi(jwt, setAndStoreJwt, `quizzes/admin/${quiz.courseSlug}/${quiz.quizSlug}/images/edit/${image.id}/`, 'POST', {
                        caption: image.caption,
                        order: imageIdx
                    });
                }
                if(!res?.ok){
                    throw new Error('Failed to save question images');
                }
            });
        } catch(e) {
            setError(true);
            console.error('Failed to save question images', JSON.stringify(questionData, null, 2), e);
        }
    }

    async function saveQuiz() {
        if(!modified) return;
        setError(false);
        await Promise.all(deletedQuestions.map(async (question) => {
            await deleteQuestion(question);
        }));
        
        await Promise.all(questionData.map(async (question, idx) => {
            if (question.id === ID_SET_ON_SERVER) {
                await createQuestion(question, idx);
            } else {
                await saveQuestion(question, idx);
            }
            if(question.images.length > 0) await saveQuestionImages(question, idx);

        }));

        await updateQuiz();
        if(!error){
            setDeletedQuestions([]);
            setModified(false);
            props.fetchQuiz();
        } else {
            console.log('ERROR');
        }

    }

    const saveChanges = () => {
        saveQuiz();
    };


    return (
        <div className="sticky_header">
            <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center'}}>
                <div> 
                    <h2>{`Editing ${quiz.name}`}</h2>
                </div>
                <div style={{display: 'flex', height: '70%', flexDirection: 'row', gap: '3px'}}>
                    <Button icon="pi pi-save" label={modified ? 'Save': 'No Changes'} disabled={!modified} raised={modified} onClick={saveChanges}/>
                    <Button icon="pi pi-undo" label="Undo Changes" disabled={!modified} severity="secondary" onClick={undoChanges}/>
                    <Button icon="pi pi-trash" label="Delete Quiz" severity="danger"/>
                </div>
            </div>
        </div>
    );
}

function AddQuestionButton({ addQuestion }: { addQuestion: () => void }) {
    return (
        <Button label="Add Question" onClick={addQuestion} />
    );
}

function serializeQuestionData(questionData: StaffQuestionData, idx: number) {
    console.log(questionData);
    const base = {
        prompt: questionData.prompt,
        render_prompt_as_latex: questionData.renderPromptAsLatex,
        points: questionData.totalMarks,
        order: idx+1,
        question_type: questionData.serverQuestionType.toLowerCase(),
    };   
    switch(questionData.questionType) {
    case 'CODE':
        return {
            ...base,
            starter_code: questionData.starterCode,
            programming_language: questionData.programmingLanguage,
            files: questionData.filesToPull,
            file_to_replace: questionData.fileToReplace,
            grading_file_directory: questionData.gradingDirectory
        };
    case 'SELECT':
        return {
            ...base,
            options: questionData.options,
            correct_option_index: questionData.correctAnswerIdx
        };
    case 'TEXT':
        return base;
    case 'MULTI_SELECT':
        return {
            ...base,
            options: questionData.options,
            correct_option_indices: questionData.correctAnswerIdxs
        };
    default:
        throw new Error(`Unsupported question type: ${JSON.stringify(questionData)}`);
    }
}

function serializeQuizData(quiz: StaffQuizProps) {
    return {
        visible_at: Math.floor(quiz.visibleAt.getTime() / 1000),
        starts_at: Math.floor(quiz.startTime.getTime() / 1000),
        ends_at: Math.floor(quiz.endTime.getTime() / 1000),
        release_at: Math.floor(quiz.releaseTime.getTime() / 1000),
        title: quiz.name,
        slug: quiz.quizSlug,
    };
}

function createImageBody(image: QuestionImage, questionData : StaffQuestionData, idx: number) {
    if(!image.file){
        console.log('No image file');
        return null;
    }
    const body = new FormData();
    body.append('question_id', questionData.id);
    body.append('question_type', questionData.serverQuestionType);
    body.append('caption', image.caption);
    body.append('order', idx.toString());
    body.append('image', image.file);
    console.log('FLAG' + JSON.stringify(body, null, 2));
    for (let pair of body.entries()) {
        console.log(`${pair[0]}:`, pair[1]);
    }
    return body;
}