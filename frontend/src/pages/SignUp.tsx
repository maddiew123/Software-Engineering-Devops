import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../styling/Login.css"
import { Select,  MenuItem, Box, TextField } from "@mui/material";
import HeaderComponent from "../components/HeaderComponent";
import type { SelectChangeEvent } from '@mui/material/Select';
import type { Team } from "../interfaces";
export default function SignUp() {
  const [teamList, setTeamList] = useState<Team[]>([]);
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
  const [form, setForm] = useState({
    username: "",
    password: "",
    full_name: "",
    email: "",
    team_id: "",
    role: "user"
  });
  const navigate = useNavigate();
  const [message, setMessage] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };
 

const handleSelectChange = (e: SelectChangeEvent) => {
  setForm({ ...form, [e.target.name]: e.target.value });
};

  const handleSubmit = async (e: React.FormEvent) => {
    console.log("wert")
    e.preventDefault();
    navigate("/")

    try {
      const payload = {
        ...form,
        team_id: form.team_id ? Number(form.team_id) : undefined,
      };

      const response = await axios.post("http://127.0.0.1:8000/signup", payload);
      setMessage(`User created! Username: ${response.data.username}`);
    } catch (error: any) {
      setMessage(error.response?.data?.detail || "Failed to create user");
    }
  };

  return (
    <>
     <HeaderComponent admin={false} loggedIn={false} />
    <Box className={"box"}>
      <h1 className="title">Sign Up</h1>
      <p>Username:</p>
      <TextField variant="outlined" name="username" placeholder="Username" onChange={handleChange} required />
      <p>Password:</p>
      <TextField variant="outlined" name="password" placeholder="Password" type="password" onChange={handleChange} required />
      <p>Full Name:</p>
      <TextField variant="outlined" name="full_name" placeholder="Full Name" onChange={handleChange} required />
      <p>Email:</p>
      <TextField variant="outlined" name="email" placeholder="Email" type="email" onChange={handleChange} required />
      <p>Team:</p>
      <Select name="team_id"
        style={{width:"56%", color:"black"}}
        label="TeamName"
        onChange={handleSelectChange}
      >
   
        {teamList.map((team, index) => {

          if (!team) return null;
          return <MenuItem value={index + 1}>{team.team_name}</MenuItem>

        })}

      </Select>
      <button onClick={handleSubmit}>Sign Up</button>

      {message && <p>{message}</p>}
    </Box>
    </>
  );
}
