import { Box, Button, MenuItem, Modal, Snackbar, TextField } from "@mui/material";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import type { Dayjs } from "dayjs";
import dayjs from "dayjs";
import React, { useEffect } from "react";
import { useState } from "react";
import Select, { type SelectChangeEvent } from '@mui/material/Select';
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../styling/MatchInput.css"
import type {Team} from "../interfaces"

export default function MatchInput({ num, index, inlocation, indate, inopponent, inhome, admin, handleUpdate }: { num?: number, index?: number, inlocation: string; indate: Dayjs | null; inopponent: number; inhome: number, admin:boolean, handleUpdate?: (index: number, updatedMatch?: any) => void; }) {
    const [teamList, setTeamList] = useState<Team[]>([]);
    const [location, setLocation] = useState(inlocation);
    const [date, setDate] = React.useState<Dayjs | null>(indate);
    const [opponent, setOpponent] = useState(inopponent);
    const [home, setHome] = useState(inhome);

   
  

    useEffect(() => {
        const fetchUserMatches = async () => {
            try {

                const res = await fetch(`http://localhost:8000/team/`);
                const data = await res.json();
                setTeamList(data.Teams);

            } catch (error) {
                console.error("Error fetching team name:", error);
            }
        };

        fetchUserMatches()
    }, [])


    const navigate = useNavigate();

    const postMatch = async () => {
        if (!index ) {
            try {
                const data = {
                    location: location,
                    date: date?.format('YYYY-MM-DD'),
                    opponent_team_id: opponent,
                    home_team_id: home,
                }
                const response = await axios.post('http://127.0.0.1:8000/match/create', data)
                console.log('Match Created:', response.data);
                setConfirm(true)
                handleClose()
                navigate("/profile")
            } catch (error) {
                console.error('Error creating match:', error);
            }

        }
        else {
            try {
                const data = {
                    location: location,
                    date: date?.format('YYYY-MM-DD'),
                    opponent_team_id: opponent,
                    home_team_id: home,
                }
                const response = await axios.put(`http://127.0.0.1:8000/match/update/${index}`, data)
                console.log('Match Updated:', response.data);

                if (handleUpdate && num) {
                    handleUpdate(num, data);

                }

                setConfirm(true)
                handleClose()
            } catch (error) {
                console.error('Error updating match:', error);
            }
        }
    }

    const deleteMatch = async () => {
        try {
            const response = await axios.delete(`http://127.0.0.1:8000/match/delete/${index}`);
            navigate("/profile")
            console.log('Match deleted:', response.data);
            if (handleUpdate && num) {
                    handleUpdate(num);

                }
            setConfirm(true)
            handleClose()
        } catch (error) {
            console.error('Error deleting match:', error);
        }

    }
    const [confirm, setConfirm] = useState(false)
    const [open, setOpen] = React.useState(false);
    const [method, setMethod] = React.useState("");
    const handleOpen = (method: string) => {
        setMethod(method);
        setOpen(true);

    };
    const handleClose = () => {
        setOpen(false);
    };

    const [action, setAction] = useState("")
    useEffect(() => {
        if (!index) {
            setAction("Create New");
        } else {
            setAction("Update");
        }
    }, [index]);

    return (
        <div className="card">
            {(admin)?
            <>

            <h1>{action} Match</h1>

            <TextField onChange={(e) => setLocation(e.target.value)} label="Location" value={location} />

            <LocalizationProvider dateAdapter={AdapterDayjs}><DatePicker label="Date" value={dayjs(date)}
                onChange={(newDate) => setDate(newDate)} /></LocalizationProvider>

            {teamList ?
                <>
                    <Select
                        value={opponent.toString()}
                        label="Opponent"
                        onChange={(event: SelectChangeEvent) => {
                            setOpponent(parseInt(event.target.value))
                        }}
                    >
                        {teamList.map((team, index) => {

                            if (!team) return null;
                            return <MenuItem value={index + 1}>{team.team_name}</MenuItem>

                        })}

                    </Select>


                    <Select

                        value={home.toString()}
                        label="Home Team"

                        onChange={(event: SelectChangeEvent) => {
                            setHome(parseInt(event.target.value))
                        }}
                    >
                        {teamList.map((team, index) => {

                            return <MenuItem value={index + 1}>{team.team_name}</MenuItem>

                        })}

                    </Select>
                </>
                : <p>error fetching teams</p>}


            <button onClick={() => handleOpen("create")}>{action}</button>
            {(index) && (
                <button onClick={() => handleOpen("delete")}>Delete</button>
            )}

            <Modal
                open={open}
                onClose={handleClose}
                aria-labelledby="child-modal-title"
                aria-describedby="child-modal-description"
            >
                <Box className="box">
                    {(method == "create") ?
                        <>
                            <p>
                                Are you sure you want to {action} match
                            </p>
                            <Button onClick={postMatch}>Yes</Button>
                            <Button onClick={handleClose}>Cancel</Button>
                        </> : <>
                            <p>
                                Are you sure you want to Delete this match
                            </p>
                            <Button onClick={deleteMatch}>Yes</Button>
                            <Button onClick={handleClose}>Cancel</Button>
                        </>}
                </Box>
            </Modal>
            {(method == "create") ?
                <Snackbar
                    open={confirm}
                    autoHideDuration={60}
                    onClose={handleClose}
                    message={action}
                /> : <Snackbar
                    open={confirm}
                    autoHideDuration={60}
                    onClose={handleClose}
                    message="Match Deleted"
                />}
</>
            : <p>you do not have access</p>}
        </div>
    );
}

