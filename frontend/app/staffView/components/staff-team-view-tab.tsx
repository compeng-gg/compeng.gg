import React, { useEffect, useState, useCallback } from 'react';
import { fetchApi } from '@/app/lib/api';
import { JwtContext } from '@/app/lib/jwt-provider';
import { Button } from 'primereact/button';
import { Dropdown } from 'primereact/dropdown';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Message } from 'primereact/message';

export interface Team {
	id: string;
	name: string;
	members: TeamMember[];
}

export interface Student {
	id: string;
	name: string;
	email: string; // Include email if needed
}

export interface TeamMember {
	id: string;
	name: string;
	role: string; // Leader or Member
}

export default function StaffTeamViewTab({ courseSlug }: { courseSlug: string }) {
    const [jwt, setAndStoreJwt] = React.useContext(JwtContext);
    const [teams, setTeams] = useState<Team[]>([]);
    const [students, setStudents] = useState<Student[]>([]);
    const [selectedLeader, setSelectedLeader] = useState<string | null>(null); // For creating teams
    const [selectedStudentToAdd, setSelectedStudentToAdd] = useState<string | null>(null); // For adding team members
    const [selectedMemberToRemove, setSelectedMemberToRemove] = useState<string | null>(null); // For removing team members

    // Fetch teams and students
    const fetchTeamsAndStudents = useCallback(async () => {
        try {
            const teamResponse = await fetchApi(jwt, setAndStoreJwt, `teams/get/${courseSlug}`, 'GET');
            const teamData = await teamResponse.json();
            setTeams(teamData);
    
            const studentResponse = await fetchApi(jwt, setAndStoreJwt, `offering/students/${courseSlug}`, 'GET');
            const studentData = await studentResponse.json();
            setStudents(studentData);
        } catch (error) {
            console.error('Error fetching teams or students:', error);
        }
    }, [jwt, setAndStoreJwt, courseSlug, setTeams, setStudents]);    

    // Call the fetch function inside useEffect
    useEffect(() => {
        fetchTeamsAndStudents();
    }, [courseSlug, jwt, setAndStoreJwt, fetchTeamsAndStudents]);

    // Create a new team with a selected leader
    const createTeam = async () => {
        if (!selectedLeader) return;
        try {
            await fetchApi(jwt, setAndStoreJwt, 'teams/admin/create/', 'POST', {
                team_name: `Team ${teams.length + 1}`,
                leader_id: selectedLeader,
                course_slug: courseSlug,
            });
            setSelectedLeader(null);
            fetchTeamsAndStudents(); // Refresh data
        } catch (error) {
            console.error('Error creating team:', error);
        }
    };

    // Add a member to a team
    const addTeamMember = async (teamId: string) => {
        if (!selectedStudentToAdd) return;
        try {
            await fetchApi(jwt, setAndStoreJwt, 'teams/admin/add/', 'POST', {
                team_id: teamId,
                member_id: selectedStudentToAdd,
            });
            setSelectedStudentToAdd(null);
            fetchTeamsAndStudents(); // Refresh data
        } catch (error) {
            console.error('Error adding team member:', error);
        }
    };

    // Remove a member from a team
    const kickTeamMember = async (teamId: string) => {
        if (!selectedMemberToRemove) return;
        try {
            await fetchApi(jwt, setAndStoreJwt, 'teams/admin/remove/', 'DELETE', {
                team_id: teamId,
                member_id: selectedMemberToRemove,
            });
            setSelectedMemberToRemove(null);
            fetchTeamsAndStudents(); // Refresh data
        } catch (error) {
            console.error('Error removing team member:', error);
        }
    };

    // Delete a team
    const deleteTeam = async (teamId: string) => {
        try {
            await fetchApi(jwt, setAndStoreJwt, 'teams/admin/delete/', 'DELETE', { team_id: teamId });
            fetchTeamsAndStudents(); // Refresh data
        } catch (error) {
            console.error('Error deleting team:', error);
        }
    };

    // Actions for each team
    const actionsTemplate = (team: Team) => {
        // Filter students who are not in any team
        const availableStudentsToAdd = students.filter(
            (student) => !teams.some((otherTeam) => otherTeam.members.some((member) => member.id === student.id))
        );

        return (
            <div>
                {/* Add Member Section */}
                <div style={{ marginBottom: '10px' }}>
                    <label>Select student to add:</label>
                    <Dropdown
                        value={selectedStudentToAdd}
                        options={availableStudentsToAdd.map((s) => ({ label: s.name, value: s.id }))}
                        placeholder="Select student"
                        onChange={(e) => setSelectedStudentToAdd(e.value)}
                    />
                    <Button
                        label="Add Member"
                        icon="pi pi-user-plus"
                        onClick={() => addTeamMember(team.id)}
                        disabled={!selectedStudentToAdd}
                        style={{ marginTop: '10px' }}
                    />
                </div>

                {/* Remove Member Section */}
                <div style={{ marginBottom: '10px' }}>
                    <label>Select member to remove:</label>
                    <Dropdown
                        value={selectedMemberToRemove}
                        options={team.members.map((m) => ({ label: m.name, value: m.id }))}
                        placeholder="Select member"
                        onChange={(e) => setSelectedMemberToRemove(e.value)}
                    />
                    <Button
                        label="Remove Member"
                        icon="pi pi-user-minus"
                        onClick={() => kickTeamMember(team.id)}
                        disabled={!selectedMemberToRemove}
                        style={{ marginTop: '10px' }}
                    />
                </div>

                {/* Delete Team Button */}
                <Button
                    label="Delete Team"
                    icon="pi pi-trash"
                    className="p-button-danger"
                    onClick={() => deleteTeam(team.id)}
                    style={{ marginTop: '10px' }}
                />
            </div>
        );
    };

    // Dropdown for selecting a leader (exclude students already in teams)
    const studentsNotInTeams = students.filter(
        (student) => !teams.some((team) => team.members.some((member) => member.id === student.id))
    );

    return (
        <div>
            <h2>Staff Team Management</h2>
            <div style={{ marginBottom: '20px' }}>
                <label>Select leader to create a team:</label>
                <Dropdown
                    value={selectedLeader}
                    options={studentsNotInTeams.map((s) => ({ label: s.name, value: s.id }))}
                    placeholder="Select leader"
                    onChange={(e) => setSelectedLeader(e.value)}
                />
                <Button
                    label="Create Team"
                    icon="pi pi-plus"
                    onClick={createTeam}
                    disabled={!selectedLeader}
                    style={{ marginTop: '10px' }}
                />
            </div>
            <DataTable value={teams}>
                <Column field="name" header="Team Name" />
                <Column
                    field="members"
                    header="Members"
                    body={(team: Team) =>
                        team.members.map((member) => (
                            <div key={member.id}>
                                {member.name} ({member.role})
                            </div>
                        ))
                    }
                />
                <Column header="Actions" body={actionsTemplate} />
            </DataTable>
        </div>
    );
}