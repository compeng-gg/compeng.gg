import { TabMenu } from 'primereact/tabmenu';
import { Lab } from '../[courseSlug]/[offeringSlug]/page';
import { useState } from 'react';
import PrimeWrapper from '../ui/primeWrapper';
import 'primeicons/primeicons.css';
import { Button } from 'primereact/button';
import StudentAssignmentTab from './components/student-assignment-tab';
import StudentTeamViewTab from './components/student-team-view-tab';
import StudentQuizViewTab from './components/student-quizzes-view-tab';
import { Console } from 'console';



export interface StudentViewProps {
    courseName: string;
    labs: Lab[];
    courseSlug: string;
    offeringSlug: string;
    teamsEnabled: boolean;
}

export default function StudentView(props: StudentViewProps){
    const {courseName, labs, courseSlug, offeringSlug, teamsEnabled} = props;

    const [idx, setIdx] = useState<number>(0);
    var items = [
        { label: 'Assignments', icon: 'pi pi-list-check'},
        { label: 'Exercises', icon: 'pi pi-check-circle'},
        { label: 'Quizzes', icon: 'pi pi-pencil'},
    ];
    if (teamsEnabled) {
        items.push({ label: 'Teams', icon: 'pi pi-users'});
    }

    return (
        <>
            <h2>{courseName}</h2>
            <PrimeWrapper>
                <TabMenu
                    model = {items}
                    activeIndex={idx}
                    onTabChange={(e) => setIdx(e.index)}
                />
                <DisplayCourseTab idx={idx} labs={labs} courseSlug={courseSlug} offeringSlug={offeringSlug}/>
            </PrimeWrapper>
        </>
    );
}

function DisplayCourseTab({idx, labs, courseSlug, offeringSlug} :{idx: number, labs: Lab[], courseSlug: string, offeringSlug: string}){

    if(idx == 0){
        return <StudentAssignmentTab labs={labs}/>;
    }
    if(idx == 2){
        return <StudentQuizViewTab courseSlug={courseSlug} offeringSlug={offeringSlug} />;
    }
    if(idx == 3){
        return <StudentTeamViewTab courseSlug={courseSlug} offeringSlug={offeringSlug}/>;
    }

    return (
        <WIP/>
    );
}

function WIP(){
    return (
        <h4>This is a work in progress</h4>
    );
}