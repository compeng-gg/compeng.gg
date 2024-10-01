import React, { ReactNode, useEffect, useState } from "react";
import { DataView, DataViewLayoutOptions } from 'primereact/dataview';
import { Card } from "primereact/card";
import { Button } from "primereact/button";
import PrimeWrapper from "@/app/components/primeWrapper";
import { DataTable, DataTableFilterMeta } from "primereact/datatable";
import { Column } from "primereact/column";
import { Tag } from "primereact/tag";
import { InputText } from 'primereact/inputtext';
import { IconField } from 'primereact/iconfield';
import { InputIcon } from 'primereact/inputicon';
import { FilterMatchMode } from "primereact/api";
import { Message } from "primereact/message";
import { Divider } from "primereact/divider";
import { Panel } from "primereact/panel";



export interface StudentTeamViewTabProps {
    courseId: string,
    userId: "seb",
}

export type TeamMembershipStatus = "leader" | "member" | "requested";

export interface TeamMembership {
    user: string;
    status: TeamMembershipStatus;
}

export interface Team {
    id: string;
    name: string;
    members: TeamMembership[];
}

const defaultData: Team[] = [
    {id: "Team 1", name: "Team 1", members: [{user: "Nick", status: "leader"}, {user: "Will", status: "member"}]},
    {id: "Team 2", name: "Team 2", members: [{user: "Abdullah", status: "leader"}, {user: "Zaid", status: "requested"}]},
    {id: "Team 3", name: "Team 3", members: [{user: "Seb", status: "leader"}, {user: "Kat", status: "member"}, {user: "Santiago", status: "requested"}, {user: "Kris", status: "requested"}]}
];


export default function StudentTeamViewTab(props: StudentTeamViewTabProps){

    const {courseId, userId} = props;

    const [teams, setTeams] = useState<Team[]>([]);

    const [userTeam, setUserTeam] = useState<Team | undefined>(defaultData[2]);

    const [userMembershipStatus, setUserMembershipStatus] = useState<TeamMembershipStatus | undefined>("leader");

    useEffect(() => {
        async function fetchTeams() {
            try {
                //eventually call API here

                setTeams(defaultData);
            } catch (error) {
                console.error("Failed to retrieve teams", error)
            }
        }

        fetchTeams()
    })

    const memberColumnTemplate = (team : Team) => {
        return (
        <TeamMemberList showLabel={false} members={team.members} />)
    }

    const joinTeam = ({team} : {team: Team}) => {
        setUserTeam(team);
        setUserMembershipStatus("requested");
    }

    const actionsColumnTemplate = (team: Team) => {
        if(team.name == userTeam?.name){
            return (<LeaveTeamButton status={userMembershipStatus} leaveTeam={leaveTeam}/>)
        }
        return (
            <Button size="small" label="Join Team" raised text onClick={() => joinTeam({team})}/>
        )
    }

    const [globalFilterValue, setGlobalFilterValue] = useState<string>('');
    const [filters, setFilters] = useState<DataTableFilterMeta>({
        global: {value: null, matchMode: FilterMatchMode.CONTAINS}
    })

    const onGlobalFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        let _filters = { ...filters };

        // @ts-ignore
        _filters['global'].value = value;

        setFilters(_filters);
        setGlobalFilterValue(value);
    };

    const renderHeader = () => {
        return (
            <div className="flex justify-content-end">
                <IconField iconPosition="left">
                    <InputIcon className="pi pi-search" />
                    <InputText value={globalFilterValue} onChange={onGlobalFilterChange} placeholder="Keyword Search" />
                </IconField>
            </div>
        );
    };

    const leaveTeam = () => {
        setUserTeam(undefined);
        setUserMembershipStatus(undefined);
    }

    const header = renderHeader();

    


    return(
        <div style={{display: "flex", flexDirection: "column", gap: "8px"}}>
            <UserTeamStatus
                team={userTeam}
                userStatus={userMembershipStatus}
                leaveTeam={leaveTeam}
            />
            <DataTable
                value={teams}
                tableStyle={{minWidth: '50rem'}}
                sortField="name"
                resizableColumns
                header={header}
                filters={filters}
                filterDisplay="row"
                globalFilterFields={['name', 'members']}>
                <Column field="name" header="Name"></Column>
                <Column field="members" header="Members" body={memberColumnTemplate}></Column>
                <Column header="Actions" body={actionsColumnTemplate}></Column>
            </DataTable>
        </div>
    )
}

export interface LeaveTeamButtonProps {
    status: TeamMembershipStatus | undefined;
    leaveTeam: () => void;
}

const LeaveTeamButton = (props: LeaveTeamButtonProps) => {
    const {status, leaveTeam} = props;
    
    if(status == undefined) return null;
    var mssg = "";
    if(status == "member") mssg = "Leave Team"
    else if (status == "leader") mssg = "Delete Team"
    else if (status == "requested") mssg = "Withdraw Request"
    return  (<Button size="small" label={mssg} raised text severity="danger" onClick={leaveTeam} />)
}

export interface UserTeamStatusProps {
    team: Team | undefined;
    userStatus: TeamMembershipStatus | undefined;
    leaveTeam: () => void;
}

const UserTeamStatus = (props: UserTeamStatusProps) => {
    const {team, userStatus, leaveTeam} = props;

    if(team  == undefined || userStatus == undefined){
        return (<Message severity="warn" text="You are not a member of any team. Please create a team or join a team from the list below" />)
    }

    const Wrapper = ({children}: {children: ReactNode}) => {
        return  (<div style={{display: "flex", flexDirection: "row", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap"}}>
            {children}</div>);
    }

    const JoinRequestList = ({team}: {team: Team}) => {
        return (
            <div style={{display: "flex", flexDirection: "column", maxWidth: "fit-content", gap: "8px"}}>
            {team.members.map((m: TeamMembership)=>{
                if(m.status != "requested"){
                    return null;
                }
                const displayString = `${m.user} has requested to join your team`;
                return (
                    <Message content={(
                        <div className="flex" style={{alignItems: "center", gap: "8px", justifyContent: "space-between", width: "100%"}}>
                            <div>{displayString}</div>
                            <div>
                                <Button icon="pi pi-check" text style={{padding: "0"}}/>
                                <Button icon="pi pi-times" text style={{padding: "0"}}/>
                            </div>
                        </div>
                    )}/>

                )
            })}
            </div>
        )
    }
    

    if(userStatus == "member"){
        return (
            <Wrapper>
                <h3>You are a member of {team.name}</h3>
                <TeamMemberList showLabel members={team.members}/>
                <LeaveTeamButton status={userStatus} leaveTeam={leaveTeam}/>    
            </Wrapper>

        )
    } else if (userStatus == "requested"){
        return (
            <Wrapper>
                <h3>You have requested to join {team.name}</h3>
                <TeamMemberList showLabel members={team.members}/>
                <LeaveTeamButton status={userStatus} leaveTeam={leaveTeam}/>
            </Wrapper>
        )
    } else if (userStatus == "leader"){
        return (
            <>
            <Wrapper>
                <h3>You are the leader of {team.name}</h3>
                <TeamMemberList showLabel members={team.members}/>
                <LeaveTeamButton status={userStatus} leaveTeam={leaveTeam}/>
            </Wrapper>
            <JoinRequestList team={team} />
            </>
        )
    }
}


const TeamMemberList = ({members, showLabel} : {members : TeamMembership[], showLabel: boolean}) => {
    return (
        <div style={{display: "flex", flexDirection: "inherit", gap: "5px"}}>
            {showLabel ? <p>Team Members: </p> : null}
            {members.map((m) => {
            //don't display member requests
            if(m.status == "requested") return null;
            const ret : string = m.user.charAt(0).toUpperCase() + m.user.slice(1);
            if(m.status == "leader"){
                return (<p><b>{ret}</b></p>)
            }
            return (<p>{ret}</p>)})}
        </div>
    )
}
