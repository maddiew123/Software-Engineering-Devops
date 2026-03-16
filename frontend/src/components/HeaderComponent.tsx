import { useNavigate } from "react-router-dom";
import  "../styling/HeaderComponent.css"
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import AdminOptions from "./AdminOptions";
import PersonIcon from '@mui/icons-material/Person';
import LogoutIcon from '@mui/icons-material/Logout';
import axios from "axios";
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";


export default function HeaderComponent({admin, loggedIn}:{admin:boolean,loggedIn:boolean}) { 
    const navigate = useNavigate()
    const signOut = () => {
         axios
    .post(`${API_BASE_URL}/logout`, {}, { withCredentials: true })
    .then(() => {
      navigate("/login");
    })
    .catch((error) => {
      console.log(error, "logout error");
    });
};

return (
    <Box className="header">
      <AppBar position="static" color="transparent">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }} style={{color:"white"}}>
            Hockey Team
          </Typography>
          {(admin)&& <AdminOptions />}
          {(loggedIn) && <><button className="actions" onClick={myMatches}><PersonIcon/>My Matches</button><button className="signOut" onClick={signOut}><LogoutIcon/>sign out</button></>}
          
        </Toolbar>
      </AppBar>
    </Box>
   
)

}
