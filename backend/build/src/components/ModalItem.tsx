import { Modal, Tooltip } from "@mui/material";
import { useState } from "react";
import MatchInput from "./MatchInput";
import EditNoteIcon from '@mui/icons-material/EditNote';
import type { Match } from "../interfaces";
import dayjs from "dayjs";
export default function ModalItem({ num, index, match, admin, handleUpdate }: { num: number, index: number; match: Match,admin:boolean, handleUpdate: (index: number, updatedMatch: Match) => void; }) {

  const [open, setOpen] = useState(false);
  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);


  return (
    <div>
      <Tooltip title="Edit Match Details">
      <button onClick={handleOpen}>
        <EditNoteIcon/>
      </button>
      </Tooltip>
      <Modal
        open={open}
        onClose={handleClose}
      >
        
        
        <MatchInput num={num} index={index} inlocation={match.location} indate={dayjs(match.date)} inopponent={match.opponent_team_id} inhome={match.home_team_id} handleUpdate={handleUpdate} admin={admin}/>
      
      </Modal>
    </div>
  );
}