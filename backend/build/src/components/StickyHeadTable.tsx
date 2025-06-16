import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import EditNoteIcon from '@mui/icons-material/EditNote';
import DeleteIcon from '@mui/icons-material/Delete';
import "../styling/StickyHeadTable.css"
import axios from 'axios';
import { useEffect, useState } from 'react';
import { Modal, Box, Button, Snackbar, TextField } from '@mui/material';
import type { Team } from '../interfaces';


export default function StickyHeadTable({ rows, handleUpdate }: { rows: Array<Team>, handleUpdate: (index: number | null, updatedMatch?: any) => void; }) {


    const columns: readonly Column[] = [
        { id: 'name', label: 'Team Name', minWidth: 170 },
    ];

    interface Column {
        id: 'name';
        label: string;
        minWidth?: number;
        align?: 'right';
        format?: (value: number) => string;
    }



    return (
        <Paper>
            <ActionButtons handleUpdate={handleUpdate} />
            <TableContainer sx={{ maxHeight: 440 }}>
                <Table stickyHeader aria-label="sticky table">
                    <TableHead>
                        <TableRow>
                            {columns.map((column) => (
                                <TableCell
                                    key={column.id}
                                    align={column.align}
                                    style={{ minWidth: column.minWidth }}
                                >
                                    {column.label}
                                </TableCell>
                            ))}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {rows.map((row, index) => (
                            <TableRow key={row.team_id}>
                                <TableCell className="cell" component="th" scope="row">
                                    {row.team_name}
                                    <ActionButtons index={index} info={row} handleUpdate={handleUpdate} />
                                </TableCell>
                            </TableRow>
                        ))}

                    </TableBody>
                </Table>
            </TableContainer>
        </Paper>
    );
}

export function ActionButtons({ info, index, handleUpdate }: { info?: Team, index?: number, handleUpdate: (index: number | null, updatedMatch?: any) => void; }) {


    const key = info?.team_id
    const [teamName, setTeamName] = useState(info?.team_name)
    const [confirm, setConfirm] = useState(false)
    const [open, setOpen] = useState(false);
    // const [method, setMethod] = useState("");
    const handleOpen = (method: string) => {
        setTeamName(info?.team_name || "");
        console.log("click", method)
        console.log("i", open)
        setAction(method);
        if (method == "delete") {

            setOpenChild(true)

        } else {
            console.log("doing", method)
            setOpen(true);

        }
        console.log("ij", open)




    };
    useEffect(() => {
        console.log("Modal open:", open);
    }, [open]);
    const handleClose = () => {
        console.log("happening")
        setOpen(false);
        setOpenChild(false)
    };

    const [action, setAction] = useState("")
    useEffect(() => {
        if (!key) {
            setAction("Create New");
        } else {
            setAction("Update");
        }
    }, [key]);



    const [openChild, setOpenChild] = useState(false);
    const handleCreate = (e: { preventDefault: () => void; }) => {
        e.preventDefault();
        setOpenChild(true);
    };

    const postTeam = async () => {
        if (!key) {
            try {
                const data = {
                    team_name: teamName
                }
                const response = await axios.post('http://127.0.0.1:8000/team/create', data)
                console.log('Team Created:', response.data);
                setConfirm(true)
                handleClose()

                handleUpdate(null, data)
            } catch (error) {
                console.error('Error creating match:', error);
            }

        }
        else {

            if (action == "delete" && index) {
                try {
                    const response = await axios.delete(`http://127.0.0.1:8000/team/delete/${key}`);
                    console.log('Team deleted:', response.data);
                    setConfirm(true)
                    handleClose()
                    handleUpdate(index)
                } catch (error) {
                    console.error('Error deleting team:', error);
                }
            } else {
                try {

                    const data = {
                        team_name: teamName
                    }

                    const response = await axios.put(`http://127.0.0.1:8000/team/update/${key}`, data)
                    console.log('Team Updated:', response.data);
                    setConfirm(true)
                    handleClose()
                    {(index)&&
                        handleUpdate(index, data)
                    }
                    
                    console.log("idk", open)



                } catch (error) {
                    console.error('Error updating team:', error);
                }
            }
        }
    }


    return (
        <div>
            {(key) ?
                <>

                    <button key={key} onClick={() => handleOpen('update')}>
                        <EditNoteIcon />
                    </button>
                    <button onClick={() => handleOpen('delete')}>
                        <DeleteIcon />
                    </button>

                    <Modal
                        open={open}
                        onClose={handleClose}
                        aria-labelledby="child-modal-title"
                        aria-describedby="child-modal-description"
                    >
                        <Box className="box" onClick={(e) => {
                            e.stopPropagation();
                        }}
                        >
                            <TextField onChange={(e) => setTeamName(e.target.value)} label="Team Name" value={teamName} />
                            <button onClick={handleCreate}>{action}</button>
                        </Box>
                    </Modal>
                </> :
                <div className='create'>
                    <button className='createButton' onClick={() => handleOpen("create")}>Create New Team</button>
                    <Modal
                        open={open}
                        onClose={handleClose}
                        aria-labelledby="child-modal-title"
                        aria-describedby="child-modal-description"
                    >
                        <Box className="box" onClick={(e) => {
                            e.stopPropagation();
                        }}>
                            <TextField onChange={(e) => setTeamName(e.target.value)} label="Team Name" />
                            <button onClick={handleCreate}>{action}</button>
                        </Box>
                    </Modal>
                </div>

            }


            <Modal
                open={openChild}
                onClose={handleClose}
                aria-labelledby="child-modal-title"
                aria-describedby="child-modal-description"
            >
                <Box className="box">
                    <p>
                        Are you sure you want to {action} Team
                    </p>
                    <Button onClick={postTeam}>Yes</Button>
                    <Button onClick={handleClose}>Cancel</Button>

                </Box>
            </Modal>

            <Snackbar
                open={confirm}
                autoHideDuration={60}
                onClose={handleClose}
                message={action}
            />
        </div>)
}


