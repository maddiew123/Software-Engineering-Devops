import { useEffect, useState } from "react";
import ModalItem from "./ModalItem";
import "../styling/Profile.css"
import DateIcon from "./DateIcon";
import { Modal, Box } from "@mui/material";
import AddMatchReport from "./AddMatchReport";

export default function MatchCard({ num, element, handleUpdate, admin  }: { num: number, element: any, admin: boolean, handleUpdate: (index: number, updatedMatch: any) => void; }) {
  const homeTeamName = useTeamName(element.home_team_id);
  const opponentTeamName = useTeamName(element.opponent_team_id);
  const index = element.match_id;
  const [open, setOpen] = useState(false);

  const readMore = () => {

    setOpen(true);

  };
  const handleClose = () => {
    setOpen(false);
  };


  return (
    <div key={index} className="match-card">
      <div className="match-title">
        <DateIcon date={element.date} />
        <p className="teams">{homeTeamName} VS {opponentTeamName}</p>

      </div>
      <div className="body">
        <p>Location: {element.location}</p>
        {(element.match_report)&&<p className="report" onClick={readMore}>Match Report: {element.match_report}</p>}
      </div>
      
      <div className="edit-button">
        {(admin) &&
          <ModalItem num={num} index={index} match={element} handleUpdate={handleUpdate} admin={admin}/>}

        <AddMatchReport curReport={element.match_report} num={num} index={index} handleUpdate={handleUpdate} />
      </div>
      <Modal
        open={open}
        onClose={handleClose}
        aria-labelledby="child-modal-title"
        aria-describedby="child-modal-description"
      >
        <Box className="box">
          {element.match_report}
        </Box>
      </Modal>


    </div>

  );
}

function useTeamName(team: number) {
  const [teamName, setTeamName] = useState("");
  useEffect(() => {
    const fetchTeamName = async () => {
      if (team) {
        try {
          const res = await fetch(`http://localhost:8000/team/${team}`);
          const data = await res.json();
          setTeamName(data.team_name);
        } catch (error) {
          console.error("Error fetching team name:", error);
        }
      }
    };

    fetchTeamName();
  }, [team]);

  return teamName
}
