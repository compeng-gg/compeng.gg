import QuizDisplay, { QuizProps } from '@/app/[courseSlug]/[offeringSlug]/quiz/quiz-display';
import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';
import { useContext, useEffect, useState } from 'react';

const now = new Date();
const oneHourBefore = new Date(now.getTime() - 1*60*60*1000);
const twoHoursLater = new Date(now.getTime() + 2 * 60 * 60 * 1000); // Add 2 hours in milliseconds

export interface StudentQuizViewProps {
    courseSlug: string;
    offeringSlug: string;
}

export default function StudentQuizViewTab(props: StudentQuizViewProps){
    const [jwt, setAndStoreJwt] = useContext(JwtContext);

    const [quizzes, setQuizs] = useState<QuizProps[]>([]);
    async function fetchQuizs() {
        try {
            const res = await fetchApi(jwt, setAndStoreJwt, `quizzes/list/${props.courseSlug}`, 'GET');
            const data = await res.json();

            const retQuizs: QuizProps[] = await Promise.all(
                data.map(async (quiz: any) => {
                    const startTime = new Date(quiz.start_unix_timestamp * 1000);
                    const endTime = new Date(quiz.end_unix_timestamp * 1000);
                    const releaseTime = new Date(quiz.release_unix_timestamp * 1000);

                    let grade = undefined;
                    let totalPoints = undefined;

                    if (new Date() > releaseTime) {
                        try {
                            const submissionRes = await fetchApi(
                                jwt,
                                setAndStoreJwt,
                                `quizzes/${props.courseSlug}/${quiz.slug}/submission/`,
                                'GET'
                            );
                            if (submissionRes.ok) {
                                const submissionData = await submissionRes.json();
                                grade = submissionData.grade; // Assuming API returns this field
                                totalPoints = submissionData.total_points;
                            }
                        } catch (err) {
                            console.error(`Failed to fetch student grade for ${quiz.slug}`, err);
                        }
                    }

                    return {
                        name: quiz.title,
                        grade,
                        quizSlug: quiz.slug,
                        courseSlug: props.courseSlug,
                        offeringSlug: props.offeringSlug,
                        startTime,
                        endTime,
                        releaseTime,
                        totalPoints,
                    };
                })
            );

            setQuizs(retQuizs);
        } catch (error) {
            console.error('Failed to retrieve quizzes', error);
        }
    }

    useEffect(() => {
        fetchQuizs();
    }, [props.courseSlug]);
    return (
        <div style={{ display: 'flex', gap: '20px', width: '100%', flexDirection: 'column' }}>
            {/* Ongoing Quizzes */}
            <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '8px' }}>Ongoing Quizzes</h2>
                {quizzes.filter(q => now >= q.startTime && now <= q.endTime).map((quiz) => (
                    <QuizDisplay {...quiz} key={quiz.quizSlug + '-ongoing'} />
                ))}
            </div>
    
            {/* Finished Quizzes */}
            <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '8px' }}>Finished Quizzes</h2>
                {quizzes.filter(q => now > q.endTime).map((quiz) => (
                    <QuizDisplay {...quiz} key={quiz.quizSlug + '-finished'} />
                ))}
            </div>
    
            {/* Upcoming Quizzes */}
            <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '8px' }}>Upcoming Quizzes</h2>
                {quizzes.filter(q => now < q.startTime).map((quiz) => (
                    <QuizDisplay {...quiz} key={quiz.quizSlug + '-upcoming'} />
                ))}
            </div>
        </div>
    );
}