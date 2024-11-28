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

export interface TeamMember {
  id: string;
  name: string;
  role: string; // Leader or Member
}

export default function StaffTeamViewTab({ courseSlug }: { courseSlug: string }) {
  const [jwt, setAndStoreJwt] = React.useContext(JwtContext);
  const [teams, setTeams] = useState<Team[]>([]);
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState<string | null>(null);

  // Fetch teams and students
  useEffect(() => {
    async function fetchTeamsAndStudents() {
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
    }
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
  const addTeamMember = async (teamId: string, studentId: string) => {
    try {
      await fetchApi(jwt, setAndStoreJwt, `teams/admin/add/`, "POST", {
        team_id: teamId,
        member_id: studentId,
      });
      fetchTeamsAndStudents(); // Refresh data
    } catch (error) {
      console.error("Error adding team member:", error);
    }
  };

  // Kick a member from the team
  const kickTeamMember = async (teamId: string, memberId: string) => {
    try {
      await fetchApi(jwt, setAndStoreJwt, `teams/admin/remove/`, "POST", {
        team_id: teamId,
        member_id: memberId,
      });
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
      <Dropdown
        value={selectedStudent}
        options={students.map((s) => ({ label: s.name, value: s.id }))}
        placeholder="Select student"
        onChange={(e) => addTeamMember(team.id, e.value)}
        style={{ marginBottom: "10px" }}
      />
      <Dropdown
        value={selectedStudent}
        options={team.members.map((m) => ({ label: m.name, value: m.id }))}
        placeholder="Select member"
        onChange={(e) => kickTeamMember(team.id, e.value)}
        style={{ marginBottom: "10px" }}
      />
      <Button
        label="Delete Team"
        icon="pi pi-trash"
        className="p-button-danger"
        onClick={() => deleteTeam(team.id)}
      />
    </div>
  );

  return (
    <div>
      <h2>Staff Team Management</h2>
      <div style={{ marginBottom: "20px" }}>
        <Dropdown
          value={selectedStudent}
          options={students.map((s) => ({ label: s.name, value: s.id }))}
          placeholder="Select leader"
          onChange={(e) => setSelectedStudent(e.value)}
        />
        <Button label="Create Team" icon="pi pi-plus" onClick={createTeam} />
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
