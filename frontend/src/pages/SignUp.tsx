import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../styling/Login.css";
import { Select, MenuItem, Box, TextField } from "@mui/material";
import HeaderComponent from "../components/HeaderComponent";
import type { SelectChangeEvent } from "@mui/material/Select";
import type { Team } from "../interfaces";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PASSWORD_MIN_LENGTH = 8;

interface FormErrors {
  username?: string;
  password?: string;
  full_name?: string;
  email?: string;
  team_id?: string;
}

export default function SignUp() {
  const [teamList, setTeamList] = useState<Team[]>([]);
  const [form, setForm] = useState({
    username: "",
    password: "",
    full_name: "",
    email: "",
    team_id: "",
    role: "user",
  });

  const [errors, setErrors] = useState<FormErrors>({});

  const [apiError, setApiError] = useState("");

  const [successMessage, setSuccessMessage] = useState("");

  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/team/`);
        const data = await res.json();
        setTeamList(data.Teams);
      } catch (error) {
        console.error("Error fetching teams:", error);
      }
    };
    fetchTeams();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
    setErrors((prev) => ({ ...prev, [name]: undefined }));
    setApiError("");
  };

  const handleSelectChange = (e: SelectChangeEvent) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setErrors((prev) => ({ ...prev, team_id: undefined }));
  };

  const validate = (): boolean => {
    const newErrors: FormErrors = {};

    if (form.username.trim() === "") {
      newErrors.username = "Username is required.";
    } else if (form.username.trim().length < 3) {
      newErrors.username = "Username must be at least 3 characters.";
    } else if (!/^[a-zA-Z0-9_]+$/.test(form.username)) {
      newErrors.username =
        "Username can only contain letters, numbers and underscores.";
    }

    if (form.password === "") {
      newErrors.password = "Password is required.";
    } else if (form.password.length < PASSWORD_MIN_LENGTH) {
      newErrors.password = `Password must be at least ${PASSWORD_MIN_LENGTH} characters.`;
    } else if (!/[A-Z]/.test(form.password)) {
      newErrors.password =
        "Password must contain at least one uppercase letter.";
    } else if (!/[0-9]/.test(form.password)) {
      newErrors.password = "Password must contain at least one number.";
    }

    if (form.full_name.trim() === "") {
      newErrors.full_name = "Full name is required.";
    } else if (form.full_name.trim().length < 2) {
      newErrors.full_name = "Please enter your full name.";
    }

    if (form.email.trim() === "") {
      newErrors.email = "Email address is required.";
    } else if (!EMAIL_REGEX.test(form.email)) {
      newErrors.email = "Please enter a valid email address.";
    }

    if (!form.team_id) {
      newErrors.team_id = "Please select a team.";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError("");
    setSuccessMessage("");

  
    if (!validate()) return;

    setLoading(true);

    try {
      const payload = {
        ...form,
        team_id: form.team_id ? Number(form.team_id) : undefined,
      };

      const response = await axios.post(`${API_BASE_URL}/signup`, payload);
      setSuccessMessage(
        `Account created successfully! Welcome, ${response.data.username}. Redirecting to login...`
      );

     
      setTimeout(() => navigate("/"), 2000);
    } catch (error: any) {
      const status = error.response?.status;

      if (status === 400) {
 
        setApiError(
          error.response?.data?.detail ||
            "Username or email is already registered. Please try a different one."
        );
      } else if (status === 422) {
       
        setApiError(
          "Please check your details and try again. Password must be at least 8 characters, contain an uppercase letter and a number."
        );
      } else {
        setApiError("Something went wrong. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <HeaderComponent admin={false} loggedIn={false} />
      <Box className="box">
        <h1 className="title">Sign Up</h1>

        <p>Username:</p>
        <TextField
          variant="outlined"
          name="username"
          placeholder="Username"
          value={form.username}
          onChange={handleChange}
          error={!!errors.username}
          helperText={errors.username}
          required
        />

        <p>Password:</p>
        <TextField
          variant="outlined"
          name="password"
          placeholder="Password"
          type="password"
          value={form.password}
          onChange={handleChange}
          error={!!errors.password}
          helperText={
            errors.password ||
            "Min. 8 characters, one uppercase letter and one number"
          }
          required
        />

        <p>Full Name:</p>
        <TextField
          variant="outlined"
          name="full_name"
          placeholder="Full Name"
          value={form.full_name}
          onChange={handleChange}
          error={!!errors.full_name}
          helperText={errors.full_name}
          required
        />

        <p>Email:</p>
        <TextField
          variant="outlined"
          name="email"
          placeholder="Email"
          type="email"
          value={form.email}
          onChange={handleChange}
          error={!!errors.email}
          helperText={errors.email}
          required
        />

        <p>Team:</p>
        <Select
          name="team_id"
          value={form.team_id}
          style={{ width: "56%", color: "black" }}
          onChange={handleSelectChange}
          displayEmpty
          error={!!errors.team_id}
        >
          <MenuItem value="" disabled>
            Select your team
          </MenuItem>
          {teamList.map((team) => {
            if (!team) return null;
            return (
              <MenuItem key={team.team_id} value={team.team_id}>
                {team.team_name}
              </MenuItem>
            );
          })}
        </Select>
        {errors.team_id && (
          <p className="error">{errors.team_id}</p>
        )}

    
        {apiError && <p className="error">{apiError}</p>}

        {successMessage && (
          <p style={{ color: "green" }}>{successMessage}</p>
        )}

        <button onClick={handleSubmit} disabled={loading}>
          {loading ? "Creating account..." : "Sign Up"}
        </button>
      </Box>
    </>
  );
}
