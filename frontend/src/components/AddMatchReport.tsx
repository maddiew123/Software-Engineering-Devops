import { Tooltip, Modal, TextField, Box } from "@mui/material";
import NoteAddIcon from '@mui/icons-material/NoteAdd';
import { useState } from "react";
import "../styling/AddMatchReport.css"
import axios from "axios";

export default  function AddMatchReport({curReport, index, num, handleUpdate}: {curReport:string,index:number,num:number, handleUpdate: (index: number, data: any) => void}) {
  const [report, setReport] = useState(curReport)
  const [open, setOpen] = useState(false);
  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const postReport = async (action: string) => {
    if (action == "delete") {
        setReport("")
    }    
try {
                const data = {
                    match_report: report
                }
                const response = await axios.put(`http://127.0.0.1:8000/match/report/update/${index}`, data)
                console.log('Report Updated:', response.data);
                handleUpdate(num , data)
                handleClose()
            } catch (error) {
                console.error('Error updating report:', error);
            }
        }
    return(
        <div>
 <Tooltip title="Add Match Report">
   <button onClick={handleOpen}><NoteAddIcon/></button>
</Tooltip>
     
     

        <Modal 
        open={open}
        onClose={handleClose}
      
      >
         <Box className="box">
            <p>Write Match Report:</p>
          <TextField
          id="outlined-multiline-flexible"
          label={curReport}
          multiline
          maxRows={4}
          onChange={(e) => setReport(e.target.value)}
        />
        <button onClick={() =>postReport("update")}>Save</button>
        <button onClick={() =>postReport("delete")}>Delete</button>
        </Box>
      </Modal>
       </div>

    )
}