import React, { ReactNode, useContext, useEffect, useState } from "react";
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
import { fetchApi } from "@/app/lib/api";
import { JwtContext } from "@/app/lib/jwt-provider";



export interface StudentTeamViewTabProps {
    courseSlug: string;
}

export enum TeamMembershipRole {
    Leader = "LEADER",
    Member = "MEMBER",
    Requested = "REQUESTED_TO_JOIN"
}

export interface TeamMembership {
    name: string;
    role: TeamMembershipRole;
}

export interface UserMembership {
    team: Team;
    role: TeamMembershipRole;
}

export interface Team {
    id: string;
    name: string;
    members: TeamMembership[];
}


export default function StudentTeamViewTab(props: StudentTeamViewTabProps){
    const [jwt, setAndStoreJwt] = useContext(JwtContext);

    const userName = "seb";
    const {courseSlug} = props;
    const [teams, setTeams] = useState<Team[]>([]);

    const [userMembership, setUserMembership] = useState<UserMembership | undefined>(undefined);

    useEffect(() => {
        async function fetchTeams() {
            try {
                //eventually call API here
                const res = await fetchApi(jwt, setAndStoreJwt, `teams/get/${courseSlug}`, "GET");
                const data = await res.json();
                const returnedTeams : Team[] = [];
                data.forEach(team => {
                    const newTeam = team as Team;
                    const userMember = newTeam.members.find(m => m.name == userName);
                    if(userMember != undefined){
                        setUserMembership({team: newTeam, role: userMember.role});
                    }
                    returnedTeams.push(team as Team);
                })
                setTeams(returnedTeams);
            } catch (error) {
                console.error("Failed to retrieve teams", error)
            }
        }

        fetchTeams()
    }, [courseSlug])

    const memberColumnTemplate = (team : Team) => {
        return (
        <TeamMemberList showLabel={false} members={team.members} />)
    }

    const joinTeam = ({team} : {team: Team}) => {
        //TODO
    }

    const actionsColumnTemplate = (team: Team) => {
        if(team.id === userMembership?.team.id){
            return (<LeaveTeamButton membership={userMembership} leaveTeam={leaveTeam}/>)
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

    const createTeam = () => {

    }

    const renderHeader = () => {
        return (
            <div className="flex" style={{justifyContent: "space-between"}}>
                <IconField iconPosition="left">
                    <InputIcon className="pi pi-search" />
                    <InputText value={globalFilterValue} onChange={onGlobalFilterChange} placeholder="Keyword Search" />
                </IconField>
                {(userMembership == undefined)
                    ? <Button size="small" label="Create Team" raised text onClick={createTeam} /> 
                    : null}
            </div>
        );
    };

    const leaveTeam = () => {
        //Todo
    }

    const header = renderHeader();

    


    return(
        <div style={{display: "flex", flexDirection: "column", gap: "8px"}}>
            <UserTeamStatus
                membership={userMembership}
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
    membership: UserMembership | undefined;
    leaveTeam: () => void;
}

const LeaveTeamButton = (props: LeaveTeamButtonProps) => {
    const {membership, leaveTeam} = props;
    
    if(membership == undefined) return null;
    var mssg = "";
    if(membership.role == TeamMembershipRole.Member) mssg = "Leave Team"
    else if (membership.role == TeamMembershipRole.Leader) mssg = "Delete Team"
    else if (membership.role == TeamMembershipRole.Requested) mssg = "Withdraw Request"
    return  (<Button size="small" label={mssg} raised text severity="danger" onClick={leaveTeam} />)
}

export interface UserTeamStatusProps {
    membership: UserMembership | undefined;
    leaveTeam: () => void;
}

const UserTeamStatus = (props: UserTeamStatusProps) => {
    const {membership, leaveTeam} = props;

    if(membership  == undefined){
        return (<Message severity="warn" text="You are not a member of any team. Please create a team or join a team from the list below" />)
    }

    const Wrapper = ({children}: {children: ReactNode}) => {
        return  (<div style={{display: "flex", flexDirection: "row", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap"}}>
            {children}</div>);
    }

    const JoinRequestList = ({team}: {team: Team}) => {
        return (
            <div style={{display: "flex", flexDirection: "column", maxWidth: "fit-content", gap: "8px"}}>
            {membership.team.members.map((m: TeamMembership)=>{
                if(m.role != TeamMembershipRole.Requested){
                    return null;
                }
                const displayString = `${m.name} has requested to join your team`;
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
    

    if(membership.role == TeamMembershipRole.Member){
        return (
            <Wrapper>
                <h3>You are a member of {membership.team.name}</h3>
                <TeamMemberList showLabel members={membership.team.members}/>
                <LeaveTeamButton membership={membership} leaveTeam={leaveTeam}/>    
            </Wrapper>

        )
    } else if (membership.role == TeamMembershipRole.Requested){
        return (
            <Wrapper>
                <h3>You have requested to join {membership.team.name}</h3>
                <TeamMemberList showLabel members={membership.team.members}/>
                <LeaveTeamButton membership={membership} leaveTeam={leaveTeam}/>
            </Wrapper>
        )
    } else if (membership.role == TeamMembershipRole.Leader){
        return (
            <>
            <Wrapper>
                <h3>You are the leader of {membership.team.name}</h3>
                <TeamMemberList showLabel members={membership.team.members}/>
                <LeaveTeamButton membership={membership} leaveTeam={leaveTeam}/>
            </Wrapper>
            <JoinRequestList team={membership.team} />
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
            if(m.role == TeamMembershipRole.Requested) return null;
            const ret : string = m.name.charAt(0).toUpperCase() + m.name.slice(1);
            if(m.role == TeamMembershipRole.Leader){
                return (<p><b>{ret}</b></p>)
            }
            return (<p>{ret}</p>)})}
        </div>
    )
}
