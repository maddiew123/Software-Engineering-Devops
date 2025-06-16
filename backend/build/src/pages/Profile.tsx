import { useEffect, useState } from "react";
import MatchCard from "../components/MatchCard";
import "../styling/Profile.css"
import HeaderComponent from "../components/HeaderComponent";
import { useUser } from "../useUser";

export default function Profile() {

  type Match = {
    match_id?: number;
    location: string;
    date: string;
    opponent_team_id: number;
    home_team_id: number;
    match_report: string;
  };

  const [userMatches, setUserMatches] = useState<Match[]>([]);

  const { user, loading } = useUser();

  const name = user?.full_name;
  const team = user?.team_id;
  const role = user?.role;
  const admin = role === "Manager";

  useEffect(() => {
    const fetchUserMatches = async () => {
      if (!team) return;

      try {
        const response = await fetch(
          admin
            ? "http://localhost:8000/match/"
            : `http://localhost:8000/match/team/${team}`
        );

        const data = await response.json();
        setUserMatches(admin ? data.Match : data.user_match);
      } catch (error) {
        console.error("Error fetching matches:", error);
      }
    };

    fetchUserMatches();
  }, [team, admin]);


  const handleUpdate = (
    index: number | null,
    updatedFields: Partial<Match> | null
  ) => {
    setUserMatches((prevMatches) => {
      if ((index !== null || index == 0) && updatedFields !== null) {


        const existingMatch = prevMatches[index];
        const updatedMatch = {
          ...existingMatch,
          ...updatedFields,
        };

        const newMatches = [...prevMatches];
        newMatches[index] = updatedMatch;
        return newMatches;
      }
      if ((index !== null || index == 0) && updatedFields == null) {
        setUserMatches((prevMatches) => {
          return prevMatches.filter((_, i) => i !== index);
        })
      }
      return prevMatches;
    })

  };

  return (
    <>
      <HeaderComponent admin={admin} loggedIn={true} />
      <div className="profile-container">
        {loading ? (
          <p>Loading...</p>
        ) : !user ? (
          <p>User not found. Please log in again.</p>
        ) : (


          <>
            <p>Hello {name}, welcome to your profile page</p>


            <div className="match-list">
              {(userMatches.length == 0) ?
                <p>you have no matches</p> :

                userMatches.map((match, i) => {
                  console.log(match.home_team_id)
    
                    return (
                      <>
                        <MatchCard num={i} element={match} handleUpdate={handleUpdate} admin={admin} />
                      </>
                    )
                  
                })}
            </div>
          </>
        )}
      </div>
    </>
  );
}


