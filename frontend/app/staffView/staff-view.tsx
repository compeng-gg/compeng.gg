import { TabMenu } from "primereact/tabmenu";
import { Lab } from "../[courseSlug]/page";
import { useState } from 'react';
import PrimeWrapper from "../components/primeWrapper";
import 'primeicons/primeicons.css';
import { Button } from "primereact/button";
import StudentAssignmentTab from "./components/student-assignment-tab";
import StudentTeamViewTab from "./components/student-team-view-tab";


export interface StaffViewProps {
    courseName: string;
    labs: Lab[];
}

export default function StaffView(props: StaffViewProps){
    const {courseName, labs} = props;

    const [idx, setIdx] = useState<number>(0);

    const items = [
        { label: 'Assignments', icon: 'pi pi-list-check'},
        { label: 'Exercises', icon: 'pi pi-check-circle'},
        { label: 'Tests', icon: 'pi pi-pencil'},
        { label: 'Teams', icon: 'pi pi-users'},
        { label: 'Course Settings', icon: 'pi pi-cog'}
    ]

    return (
        <>
            <h2>{courseName}</h2>
            <PrimeWrapper>
                <TabMenu
                    model = {items}
                    activeIndex={idx}
                    onTabChange={(e) => setIdx(e.index)}
                />
                <DisplayCourseTab idx={idx} labs={labs}/>
            </PrimeWrapper>
        </>
    )
}

function DisplayCourseTab({idx, labs}){
    return (
        <WIP/>
    )
}

function WIP(){
    return (
        <h4>This is a work in progress</h4>
    )
}