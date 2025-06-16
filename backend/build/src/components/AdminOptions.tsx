
import { useNavigate } from "react-router-dom";

import CreateIcon from '@mui/icons-material/Create';
import GroupsIcon from '@mui/icons-material/Groups';

export default function AdminOptions(){
    const navigate = useNavigate()
      const createNewMatch = () => {
    navigate("/match/create");
  };
  
  
  
      const editTeams = () => {
    navigate("/teams");
  };
  const actions = [
  { icon: <CreateIcon />, name: 'Create Match' ,funct: createNewMatch},
  { icon: <GroupsIcon />, name: 'Edit Teams' ,funct: editTeams},
 
];
return(
    <>
    
  {actions.map((action) => (
    <button
      key={action.name}
      onClick={action.funct}
      className="actions"
    >{action.icon}{action.name}</button>
  ))}


</>
)
    
}