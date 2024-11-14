import { TabMenu } from "primereact/tabmenu";
import { Lab } from "../[slug]/page";
import { useState } from 'react';
import PrimeWrapper from "../components/primeWrapper";
import 'primeicons/primeicons.css';
import { Button } from "primereact/button";
import StudentAssignmentTab from "./components/student-assignment-tab";
import StudentTeamViewTab from "./components/student-team-view-tab";
import StudentExamViewTab from "./components/student-exams-view-tab";



export interface StudentViewProps {
    courseName: string;
    labs: Lab[];
    courseSlug: string;
}

export default function StudentView(props: StudentViewProps){
    const {courseName, labs, courseSlug} = props;

    const [idx, setIdx] = useState<number>(0);
    const items = [
        { label: 'Assignments', icon: 'pi pi-list-check'},
        { label: 'Exercises', icon: 'pi pi-check-circle'},
        { label: 'Tests', icon: 'pi pi-pencil'},
        { label: 'Teams beta', icon: 'pi pi-users'}
    ]

    return (
    <>
    
        <h2>{courseName + "beta"}</h2>
        <PrimeWrapper>
        
            <TabMenu
                model = {items}
                activeIndex={idx}
                onTabChange={(e) => setIdx(e.index)}
            />
            <DisplayCourseTab idx={idx} labs={labs} courseSlug={courseSlug}/>
        </PrimeWrapper>
    </>
    )
}

function DisplayCourseTab({idx, labs, courseSlug}){

    if(idx == 0){
        return <StudentAssignmentTab labs={labs}/>
    }
    if(idx == 2){
        return <StudentExamViewTab />
    }
    if(idx == 3){
        return <StudentTeamViewTab  courseSlug={courseSlug}/>
    }

    return (
        <WIP/>
    )
}

function WIP(){
    return (
        <h4>This is a work in progress</h4>
    )
}