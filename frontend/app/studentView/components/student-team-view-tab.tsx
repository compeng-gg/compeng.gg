import React, { ReactNode, useContext, useEffect, useState } from "react";
import { DataView, DataViewLayoutOptions } from "primereact/dataview";
import { Card } from "primereact/card";
import { Button } from "primereact/button";
import PrimeWrapper from "@/app/components/primeWrapper";
import { DataTable, DataTableFilterMeta } from "primereact/datatable";
import { Column } from "primereact/column";
import { Tag } from "primereact/tag";
import { InputText } from "primereact/inputtext";
import { IconField } from "primereact/iconfield";
import { InputIcon } from "primereact/inputicon";
import { FilterMatchMode } from "primereact/api";
import { Message } from "primereact/message";
import { Divider } from "primereact/divider";
import { Panel } from "primereact/panel";
import { fetchApi } from "@/app/lib/api";
import { JwtContext } from "@/app/lib/jwt-provider";
import { fetchUserName } from "@/app/lib/getUser";
import { Dialog } from "primereact/dialog";

export interface StudentTeamViewTabProps {
  courseSlug: string;
}

export enum TeamMembershipRole {
  Leader = "LEADER",
  Member = "MEMBER",
  Requested = "REQUESTED_TO_JOIN",
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

export default function StudentTeamViewTab(props: StudentTeamViewTabProps) {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);
  const { courseSlug } = props;
  const [teams, setTeams] = useState<Team[]>([]);
  const [userMembership, setUserMembership] = useState<
    UserMembership | undefined
  >(undefined);
  const [userName, setUserName] = useState<string>("");

  // Fetch username on component mount
  useEffect(() => {
    fetchUserName(jwt, setAndStoreJwt)
      .then((fetchedUserName) => {
        setUserName(fetchedUserName); // Set the username in state
      })
      .catch((error) => console.error("Failed to fetch username:", error));
  }, [jwt, setAndStoreJwt]);

  // Fetch teams whenever userName is set
  useEffect(() => {
    if (userName) {
      fetchTeams();
    }
  }, [userName]);

  // Fetch teams function, accessible to all parts of the file
  const fetchTeams = async () => {
    try {
      const res = await fetchApi(
        jwt,
        setAndStoreJwt,
        `teams/get/${courseSlug}`,
        "GET"
      );
      const data = await res.json();
      const returnedTeams = [];
      let foundMembership = false;

      data.forEach((team) => {
        const userMember = team.members.find((m) => m.name === userName);
        if (userMember) {
          setUserMembership({ team, role: userMember.role });
          foundMembership = true;
        }
        returnedTeams.push(team);
      });

      if (!foundMembership) setUserMembership(undefined); // Reset membership if none found

      setTeams(returnedTeams);
    } catch (error) {
      console.error("Failed to retrieve teams", error);
    }
  };

  const memberColumnTemplate = (team: Team) => {
    return <TeamMemberList showLabel={false} members={team.members} />;
  };

  const joinTeam = ({ team }: { team: Team }) => {
    fetchApi(jwt, setAndStoreJwt, `teams/join/request/`, "PATCH", {
      team_id: team.id,
    }).then((response) => {
      console.log(response.status);
      fetchTeams();
    });
    //TODO
  };

  const actionsColumnTemplate = (team: Team) => {
    if (team.id === userMembership?.team.id) {
      return (
        <LeaveTeamButton membership={userMembership} leaveTeam={leaveTeam} />
      );
    }
    return (
      <Button
        size="small"
        label="Join Team"
        raised
        text
        onClick={() => joinTeam({ team })}
      />
    );
  };

  const [globalFilterValue, setGlobalFilterValue] = useState<string>("");
  const [filters, setFilters] = useState<DataTableFilterMeta>({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
  });

  const onGlobalFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    let _filters = { ...filters };

    // @ts-ignore
    _filters["global"].value = value;

    setFilters(_filters);
    setGlobalFilterValue(value);
  };

  const createTeam = () => {
    fetchApi(jwt, setAndStoreJwt, `teams/create/`, "POST", {
      team_name: "Team " + (teams.length + 1).toString(),
      course_slug: courseSlug,
    }).then((response) => {
      fetchTeams();
    });
  };

  const renderHeader = () => {
    return (
      <div className="flex" style={{ justifyContent: "space-between" }}>
        <IconField iconPosition="left">
          <InputIcon className="pi pi-search" />
          <InputText
            value={globalFilterValue}
            onChange={onGlobalFilterChange}
            placeholder="Keyword Search"
          />
        </IconField>
        {userMembership == undefined ? (
          <Button
            size="small"
            label="Create Team"
            raised
            text
            onClick={createTeam}
          />
        ) : null}
      </div>
    );
  };

  const leaveTeam = () => {
    console.log("Leaving team " + userMembership?.team.id);
    fetchApi(jwt, setAndStoreJwt, `teams/leave/`, "PATCH", {
      team_id: userMembership?.team.id ?? "",
    }).then((response) => {
      fetchTeams();
    });
  };

  const header = renderHeader();

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      <UserTeamStatus
        membership={userMembership}
        fetchTeams={fetchTeams}
        leaveTeam={leaveTeam}
      />
      <DataTable
        value={teams}
        tableStyle={{ minWidth: "50rem" }}
        sortField="name"
        resizableColumns
        header={header}
        filters={filters}
        filterDisplay="row"
        globalFilterFields={["name", "members"]}
      >
        <Column field="name" header="Name"></Column>
        <Column
          field="members"
          header="Members"
          body={memberColumnTemplate}
        ></Column>
        <Column header="Actions" body={actionsColumnTemplate}></Column>
      </DataTable>
    </div>
  );
}

export interface LeaveTeamButtonProps {
  membership: UserMembership | undefined;
  leaveTeam: () => void;
}

const LeaveTeamButton = (props: LeaveTeamButtonProps) => {
  const { membership, leaveTeam } = props;

  if (membership == undefined) return null;
  var mssg = "";
  if (membership.role == TeamMembershipRole.Member) mssg = "Leave Team";
  else if (membership.role == TeamMembershipRole.Leader) mssg = "Delete Team";
  else if (membership.role == TeamMembershipRole.Requested)
    mssg = "Withdraw Request";
  return (
    <Button
      size="small"
      label={mssg}
      raised
      text
      severity="danger"
      onClick={leaveTeam}
    />
  );
};

export interface UserTeamStatusProps {
  membership: UserMembership | undefined;
  fetchTeams: () => void;
  leaveTeam: () => void;
}

const UserTeamStatus = (props: UserTeamStatusProps) => {
  const [jwt, setAndStoreJwt] = useContext(JwtContext);

  const { membership, leaveTeam, fetchTeams } = props;

  if (membership == undefined) {
    return (
      <Message
        severity="warn"
        text="You are not a member of any team. Please create a team or join a team from the list below"
      />
    );
  }

  const Wrapper = ({ children }: { children: ReactNode }) => {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        {children}
      </div>
    );
  };

  const manageJoinRequest = ({ team, name, approved }) => {
    fetchApi(jwt, setAndStoreJwt, `teams/join/manage/`, "PATCH", {
      team_id: team.id,
      joiner_name: name,
      approved: approved,
    }).then((response) => {
      fetchTeams();
    });
  };

  const JoinRequestList = ({ team }: { team: Team }) => {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          maxWidth: "fit-content",
          gap: "8px",
        }}
      >
        {membership.team.members.map((m: TeamMembership) => {
          if (m.role != TeamMembershipRole.Requested) {
            return null;
          }
          const displayString = `${m.name} has requested to join your team`;
          return (
            <Message
              content={
                <div
                  className="flex"
                  style={{
                    alignItems: "center",
                    gap: "8px",
                    justifyContent: "space-between",
                    width: "100%",
                  }}
                >
                  <div>{displayString}</div>
                  <div>
                    <Button
                      icon="pi pi-check"
                      text
                      style={{ padding: "0" }}
                      onClick={() =>
                        manageJoinRequest({
                          team,
                          name: m.name,
                          approved: true,
                        })
                      }
                    />
                    <Button
                      icon="pi pi-times"
                      text
                      style={{ padding: "0" }}
                      onClick={() =>
                        manageJoinRequest({
                          team,
                          name: m.name,
                          approved: false,
                        })
                      }
                    />
                  </div>
                </div>
              }
            />
          );
        })}
      </div>
    );
  };

  if (membership.role == TeamMembershipRole.Member) {
    return (
      <Wrapper>
        <h3>You are a member of {membership.team.name}</h3>
        <TeamMemberList showLabel members={membership.team.members} />
        <LeaveTeamButton membership={membership} leaveTeam={leaveTeam} />
      </Wrapper>
    );
  } else if (membership.role == TeamMembershipRole.Requested) {
    return (
      <Wrapper>
        <h3>You have requested to join {membership.team.name}</h3>
        <TeamMemberList showLabel members={membership.team.members} />
        <LeaveTeamButton membership={membership} leaveTeam={leaveTeam} />
      </Wrapper>
    );
  } else if (membership.role == TeamMembershipRole.Leader) {
    return (
      <>
        <Wrapper>
          <h3>You are the leader of {membership.team.name}</h3>
          <TeamMemberList showLabel members={membership.team.members} />
          {membership.team.members.length == 1 ? (
            <LeaveTeamButton membership={membership} leaveTeam={leaveTeam} />
          ) : null}
        </Wrapper>
        <JoinRequestList team={membership.team} />
      </>
    );
  }
};

const TeamMemberList = ({
  members,
  showLabel,
}: {
  members: TeamMembership[];
  showLabel: boolean;
}) => {
  return (
    <div style={{ display: "flex", flexDirection: "inherit", gap: "5px" }}>
      {showLabel ? <p>Team Members: </p> : null}
      {members.map((m) => {
        //don't display member requests
        if (m.role == TeamMembershipRole.Requested) return null;
        const ret: string = m.name.charAt(0).toUpperCase() + m.name.slice(1);
        if (m.role == TeamMembershipRole.Leader) {
          return (
            <p>
              <b>{ret}</b>
            </p>
          );
        }
        return <p>{ret}</p>;
      })}
    </div>
  );
};
