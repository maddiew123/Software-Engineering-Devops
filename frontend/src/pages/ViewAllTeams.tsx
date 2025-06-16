import { useEffect, useState } from "react";

import StickyHeadTable from "../components/StickyHeadTable";
import HeaderComponent from "../components/HeaderComponent";
import { useUser } from "../useUser";
import type { Team } from "../interfaces";

export default function ViewAllTeams() {
  
    const { user, loading } = useUser();
    const role = user?.role;
    const admin = role === "Manager";
    const [allTeams, setAllTeams] = useState(Array<Team>)


    useEffect(() => {

        const fetchAllTeams = async () => {

            try {
                const response = await fetch(`http://localhost:8000/team/`);
                const data = await response.json();
                console.log("Fetched teams:", data);
                setAllTeams(data.Teams);
            } catch (error) {
                console.error("Error fetching teams:", error);
            }
        }
        fetchAllTeams();
    }, []);
    const handleUpdate = (
  index: number | null,
  updatedFields: Partial<Team> | null
) => {
      
  setAllTeams((prevTeams) => {
    
    if (index === null && updatedFields !== null) {
        const newTeam: Team = {
    team_id: 99,
    team_name: updatedFields.team_name ?? "Untitled Team",
  };
      console.log("creating");
      return [...prevTeams, newTeam]; 
      }

  
    else if ((index !== null ||index == 0) && updatedFields == null) {
      console.log("deleting");
    
      return prevTeams.filter((_, i) => i !== index);
    }


    else if ((index !== null ||index == 0) && updatedFields !== null) {
      console.log("updating");
      if (index < 0 || index >= prevTeams.length) return prevTeams;

      const existingTeam = prevTeams[index];
      const updatedTeam = {
        ...existingTeam,
        ...updatedFields,
      };

      const newTeams = [...prevTeams];
      newTeams[index] = updatedTeam;
      return newTeams;
    }


    return prevTeams;
  });

  console.log("teams:", allTeams); // Note: `allTeams` won't show updated value immediately (React state updates are async)
};



    return (
        <>
            <HeaderComponent admin={admin} loggedIn={true} />
            {loading ? (
          <p>Loading...</p>
        ) :
            (admin) ?
                <>
                    {(allTeams.length == 0) ?

                        <p>no teams</p> :


                        <StickyHeadTable rows={allTeams} handleUpdate={handleUpdate} />

                    } </> : <p>you do not have access</p>

            }

        </>
    );
}


