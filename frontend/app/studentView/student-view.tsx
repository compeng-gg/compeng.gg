import { TabMenu } from "primereact/tabmenu";
import { Lab } from "../[slug]/page";
import { useState } from 'react';
import PrimeWrapper from "../components/primeWrapper";
import 'primeicons/primeicons.css';
import { Button } from "primereact/button";



export interface StudentViewProps {
    courseName: string;
    labs: Lab[];
}

export default function StudentView(props: StudentViewProps){
    const {courseName, labs} = props;

    const [idx, setIdx] = useState<number>(0);
    const items = [
        { label: 'Assignments', icon: 'pi pi-list-check'},
        { label: 'Exercises', icon: 'pi pi-check-circle'},
        { label: 'Tests', icon: 'pi pi-pencil'},
        { label: 'Teams', icon: 'pi pi-users'}
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
        
        </PrimeWrapper>
    </>
    )
}

// function DisplayCourseTab({idx, labs}){

//     return ({null});
//     if(idx == 0){
//         return (
//             <AssignmentDisplay labs={labs} />
//         )
//     }
//     if(idx == 4){
//         return (
//             <TeamsDisplay/>
//         )
//     }
//     else {
//         return (
//             <WIP/>
//         )
//     }
// }

// function WIP(){
//     return (<
        
//     )
// }