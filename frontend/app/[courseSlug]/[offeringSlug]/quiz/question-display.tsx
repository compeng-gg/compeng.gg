import { Badge } from 'primereact/badge';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import CodeEditor from './components/code-editor';
import { isAnswered, QuestionProps } from './question-models';
import TextEditor from './components/text-editor';
import SelectEditor from './components/select-editor';
import { useContext, useEffect, useRef, useState } from 'react';
import { JwtContext } from '@/app/lib/jwt-provider';
import { fetchApi } from '@/app/lib/api';
import { QuizProps } from './quiz-display';
import MultiSelectEditor from './components/multiselect-editor';

enum QuestionSaveStatus {
    NOT_ANSWERED = 'Not Answered',
    AUTOSAVING = 'Autosaving',
    TYPING = 'Typing...',
    AUTOSAVED = 'Autosaved',
    ERROR = 'Error'
};

//Display of the question inside a container
export function QuestionDisplay(props: QuestionProps){

    // Notice we now focus on using the courseSlug:
    //   props.courseSlug
    //   props.quizSlug
    // from the question props
    const { title, prompt, totalMarks, isMutable, questionType, idx } = props;

    const [debouncedAnswer, setDebouncedAnswer] = useState<any>(props.state.value);

    const lastSavedRef = useRef<any>(props.state.value);
    const lastValueRef = useRef<any>(props.state.value);



    const MS_TO_DEBOUNCE_SAVE = 5000, MS_TO_AUTO_SAVE = 20 * 1000;

    const [status, setStatus] = useState<QuestionSaveStatus>(
        isAnswered(props) ? QuestionSaveStatus.AUTOSAVED : QuestionSaveStatus.NOT_ANSWERED
    );

    // Debounced save for TEXT/CODE questions
    useEffect(() => {
        // Only run this effect if the question type is TEXT or CODE.
        if (!(props.questionType === 'TEXT' || props.questionType === 'CODE')) return;

        // If the current value matches the last saved value, do nothing.
        if (props.state.value === lastSavedRef.current) return;

        // Update the last value reference.
        lastValueRef.current = props.state.value;

        // If the question is answered, set the status to TYPING.
        if (isAnswered(props)) {
            setStatus(QuestionSaveStatus.TYPING);
        }

        const timer = setTimeout(() => {
            setDebouncedAnswer(props.state.value);
        }, MS_TO_DEBOUNCE_SAVE);

        return () => clearTimeout(timer);
    }, [props.questionType, props.state.value]);

    useEffect(() => {
        // Only run this effect if the question type is TEXT or CODE.
        if (!(props.questionType === 'TEXT' || props.questionType === 'CODE')) return;

        if (debouncedAnswer !== lastSavedRef.current && isAnswered(props)) {
            save(debouncedAnswer);
            lastSavedRef.current = props.state.value;
        }
    }, [props.questionType, debouncedAnswer, props.state.value]);

    useEffect(() => {
        // Only run this effect if the question type is TEXT or CODE.
        if (!(props.questionType === 'TEXT' || props.questionType === 'CODE')) return;

        const interval = setInterval(() => {
            if (lastValueRef.current !== lastSavedRef.current && isAnswered(props)) {
                save(lastValueRef.current);
            }
        }, MS_TO_AUTO_SAVE);

        return () => clearInterval(interval);
    }, [props.questionType, MS_TO_AUTO_SAVE, /* include isAnswered and save if they are not stable */]);

    /**
     * Modified `save` function to use the courseSlug in the request
     * and print it whenever a question is saved.
     */
    async function save(newValue: any) {
        try {
            setStatus(QuestionSaveStatus.AUTOSAVING);

            // If it's a string, ensure it's not empty
            if (typeof newValue === 'string') {
                const trimmed = newValue.trim();
                if (!trimmed.length) {
                    setStatus(QuestionSaveStatus.NOT_ANSWERED);
                    return;
                }
            }

            // Print the course slug each time we save
            console.log('Course slug is:', props.courseSlug);

            // Quizple: Construct an API URL using courseSlug
            const apiUrl = `${props.courseSlug}/quiz/${props.quizSlug}/answer/${props.serverQuestionType.toLowerCase()}/${props.id}/?courseSlug=${props.courseSlug}`;

            const res = await fetchApi(
                jwt,
                setAndStoreJwt,
                apiUrl,
                'POST',
                getAnswerBody(props, newValue)
            );

            if (res.ok) {
                lastSavedRef.current = newValue;
                setStatus(QuestionSaveStatus.AUTOSAVED);
            } else {
                setStatus(QuestionSaveStatus.ERROR);
            }
        } catch (error) {
            console.error('Error submitting question', error);
            setStatus(QuestionSaveStatus.ERROR);
        }
    }

    const header = (
        <div style={{position: 'relative'}}>
            <span></span>
            <div style={{ position: 'absolute', top: '10px', right: '10px', display: 'flex', gap: '8px' }}>
                <StatusBadge status={status} />
                <GradeBadge grade={undefined} totalAvailable={totalMarks} />
            </div>
        </div>
    );

    return (
        <Card
            title={title ?? `Question ${idx !== undefined ? idx + 1 : ''}`}
            subTitle={prompt}
            header={header}
            footer={footer}
        >
            <QuestionContent props={props} save={save} />
        </Card>
    );
}

function QuestionContent({ props, save }: { props: QuestionProps, save: (newValue: any) => void }) {
    switch (props.questionType) {
    case 'CODE':
        return <CodeEditor props={props} save={save} />;
    case 'TEXT':
        return <TextEditor state={props.state} save={save} />;
    case 'SELECT':
        return <SelectEditor props={props} save={save} />;
    case 'MULTI_SELECT':
        return <MultiSelectEditor props={props} save={save} />;
    default:
        return null;
    }
}

function GradeBadge({ grade, totalAvailable }: { grade?: number, totalAvailable: number }) {
    const percentGrade = 100 * (grade ?? 0 / totalAvailable);
    const value: string = grade
        ? `Grade: ${grade}/${totalAvailable} (${percentGrade}%)`
        : `Points: ${totalAvailable}`;
    const severity = grade ? 'success' : 'info';

    return (
        <Badge
            size="large"
            value={`Grade: ${grade}/${totalAvailable} (${percentGrade}%)`}
            severity={"success"}
        />
    );
}

function StatusToSeverity(status: QuestionSaveStatus) {
    switch (status) {
    case QuestionSaveStatus.AUTOSAVED:
        return 'success';
    case QuestionSaveStatus.ERROR:
        return 'danger';
    case QuestionSaveStatus.NOT_ANSWERED:
        return 'secondary';
    default:
        return 'info';
    }
}

function StatusBadge({ status }: { status: QuestionSaveStatus }) {
    return (
        <Badge
            size="large"
            value={status}
            severity={StatusToSeverity(status)}
        />
    );
}

/**
 * Helper function to build the request body
 */
function getAnswerBody(props: QuestionProps, value: any) {
    switch (props.questionType) {
    case 'CODE':
        return { solution: value };
    case 'SELECT':
        return { selected_answer_index: value };
    case 'TEXT':
        return { response: value };
    case 'MULTI_SELECT':
        return { selected_answer_indices: value };
    }
}
