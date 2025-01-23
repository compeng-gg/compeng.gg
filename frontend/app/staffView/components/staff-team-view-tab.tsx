import React, { useEffect, useState } from "react";
import { fetchApi } from "@/app/lib/api";
import { JwtContext } from "@/app/lib/jwt-provider";
import { Button } from "primereact/button";
import { Dropdown } from "primereact/dropdown";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { Message } from "primereact/message";

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
  const [selectedStudent, setSelectedStudent] = useState<string | null>(null);
  const [selectedMember, setSelectedMember] = useState<string | null>(null);

  // Fetch teams and students
  const fetchTeamsAndStudents = async () => {
    try {
      const teamResponse = await fetchApi(jwt, setAndStoreJwt, `teams/get/${courseSlug}`, "GET");
      const teamData = await teamResponse.json();
      console.log("teamData", teamData);
      setTeams(teamData);

      const studentResponse = await fetchApi(jwt, setAndStoreJwt, `offering/students/${courseSlug}`, "GET");

      
      const studentData = await studentResponse.json();
      console.log("studentData", studentData);

      setStudents(studentData);
    } catch (error) {
      console.error("Error fetching teams or students:", error);
    }
  };

  // Call the fetch function inside useEffect
  useEffect(() => {
    fetchTeamsAndStudents();
  }, [courseSlug, jwt, setAndStoreJwt]);

  // Create a new team with a selected leader
  const createTeam = async () => {
    if (!selectedStudent) return;
    try {
      await fetchApi(jwt, setAndStoreJwt, `teams/create/`, "POST", {
        team_name: `Team ${teams.length + 1}`,
        leader_id: selectedStudent,
        course_slug: courseSlug,
      });
      setSelectedStudent(null);
      fetchTeamsAndStudents(); // Refresh data
    } catch (error) {
      console.error("Error creating team:", error);
    }
  };

  // Add a member to the team
  const addTeamMember = async (teamId: string) => {
    if (!selectedStudent) return;
    try {
      await fetchApi(jwt, setAndStoreJwt, `teams/admin/add/`, "POST", {
        team_id: teamId,
        member_id: selectedStudent,
      });
      setSelectedStudent(null);
      fetchTeamsAndStudents(); // Refresh data
    } catch (error) {
      console.error("Error adding team member:", error);
    }
  };

  // Kick a member from the team
  const kickTeamMember = async (teamId: string) => {
    if (!selectedMember) return;
    try {
      await fetchApi(jwt, setAndStoreJwt, `teams/admin/remove/`, "POST", {
        team_id: teamId,
        member_id: selectedMember,
      });
      setSelectedMember(null);
      fetchTeamsAndStudents(); // Refresh data
    } catch (error) {
      console.error("Error kicking team member:", error);
    }
  };

  // Delete a team
  const deleteTeam = async (teamId: string) => {
    try {
      await fetchApi(jwt, setAndStoreJwt, `teams/delete/`, "POST", { team_id: teamId });
      fetchTeamsAndStudents(); // Refresh data
    } catch (error) {
      console.error("Error deleting team:", error);
    }
  };

  const actionsTemplate = (team: Team) => (
    <div>
      <div style={{ marginBottom: "10px" }}>
        <label>Select student to add:</label>
        <Dropdown
          value={selectedStudent}
          options={students.map((s) => ({ label: s.name, value: s.id }))}
          placeholder="Select student"
          onChange={(e) => setSelectedStudent(e.value)}
        />
        <Button
          label="Add Member"
          icon="pi pi-user-plus"
          onClick={() => addTeamMember(team.id)}
          disabled={!selectedStudent}
          style={{ marginTop: "10px" }}
        />
      </div>

      <div style={{ marginBottom: "10px" }}>
        <label>Select member to remove:</label>
        <Dropdown
          value={selectedMember}
          options={team.members.map((m) => ({ label: m.name, value: m.id }))}
          placeholder="Select member"
          onChange={(e) => setSelectedMember(e.value)}
        />
        <Button
          label="Remove Member"
          icon="pi pi-user-minus"
          onClick={() => kickTeamMember(team.id)}
          disabled={!selectedMember}
          style={{ marginTop: "10px" }}
        />
      </div>

      <Button
        label="Delete Team"
        icon="pi pi-trash"
        className="p-button-danger"
        onClick={() => deleteTeam(team.id)}
        style={{ marginTop: "10px" }}
      />
    </div>
  );

  return (
    <div>
      <h2>Staff Team Management</h2>
      <div style={{ marginBottom: "20px" }}>
        <label>Select leader to create a team:</label>
        <Dropdown
          value={selectedStudent}
          options={students.map((s) => ({ label: s.name, value: s.id }))}
          placeholder="Select leader"
          onChange={(e) => setSelectedStudent(e.value)}
        />
        <Button
          label="Create Team"
          icon="pi pi-plus"
          onClick={createTeam}
          disabled={!selectedStudent}
          style={{ marginTop: "10px" }}
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