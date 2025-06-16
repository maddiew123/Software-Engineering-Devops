import { useNavigate } from "react-router-dom";
import  "../styling/HeaderComponent.css"
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import AdminOptions from "./AdminOptions";
import PersonIcon from '@mui/icons-material/Person';
import LogoutIcon from '@mui/icons-material/Logout';

export default function HeaderComponent({admin, loggedIn}:{admin:boolean,loggedIn:boolean}) { 
    const navigate = useNavigate()
    const signOut = () => {
        localStorage.removeItem("tokenya");
        navigate("/");
        loggedIn=false;
    };
    const myMatches = () => {

        navigate("/profile");
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
