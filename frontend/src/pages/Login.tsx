import axios from "axios";
import { useNavigate } from "react-router";
import { useState } from "react";
import "../styling/Login.css";
import HeaderComponent from "../components/HeaderComponent";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  // Individual field errors shown beneath each input
  const [usernameError, setUsernameError] = useState("");
  const [passwordError, setPasswordError] = useState("");

  // General error shown when the API returns 401 (wrong credentials)
  const [loginError, setLoginError] = useState("");

  // Prevents double-clicking the login button while the request is in flight
  const [loading, setLoading] = useState(false);

  const validate = (): boolean => {
    let valid = true;

    // Clear previous errors before re-validating
    setUsernameError("");
    setPasswordError("");
    setLoginError("");

    if (username.trim() === "") {
      setUsernameError("Please enter your username.");
      valid = false;
    }

    if (password.trim() === "") {
      setPasswordError("Please enter your password.");
      valid = false;
    }

    return valid;
  };

  const login = () => {
    // Run client-side validation first — stops the request if fields are empty
    if (!validate()) return;

    setLoading(true);

    axios
      .post(
        `${API_BASE_URL}/login`,
        {
          username: username,
          password_hash: password,
        },
        {
          withCredentials: true,
        }
      )
      .then((response) => {
        if (response.data.message === "login_success") {
          navigate("/profile");
        } else {
          // Fallback — shouldn't normally reach here given the backend now
          // raises HTTPException on failure rather than returning a message
          setLoginError("Login failed. Please try again.");
        }
      })
      .catch((error) => {
        if (error.response) {
          const status = error.response.status;

          if (status === 401) {
            // Backend returns 401 for invalid username or password.
            // A generic message is shown deliberately — we do not tell the
            // user which of the two was wrong, to prevent user enumeration.
            setLoginError("Invalid username or password. Please try again.");
          } else if (status === 429) {
            // Backend rate limiter (slowapi) returns 429 after 5 failed
            // attempts per minute. Inform the user to wait before retrying.
            setLoginError("Too many login attempts. Please wait a minute and try again.");
          } else if (status === 422) {
            // FastAPI returns 422 if the request body fails Pydantic validation
            setLoginError("Invalid input. Please check your details and try again.");
          } else {
            setLoginError("Something went wrong. Please try again later.");
          }
        } else {
          // Network error — no response received at all (e.g. server is down)
          setLoginError("Unable to connect to the server. Please check your connection.");
        }
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <div className="background">
      <HeaderComponent admin={false} loggedIn={false} />
      <div className="wrapper">
        <div className="box">
          <h1 className="title">Login Page</h1>

          <p>Username</p>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          {/* Show username validation error beneath the field */}
          {usernameError && <p className="error">{usernameError}</p>}

          <p>Password</p>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {/* Show password validation error beneath the field */}
          {passwordError && <p className="error">{passwordError}</p>}

          {/* Show general API error (wrong credentials, rate limit etc.) */}
          {loginError && <p className="error">{loginError}</p>}

          <button type="button" onClick={login} disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </div>

        <p className="signUp" onClick={() => navigate("/signup")}>
          Sign Up
        </p>
      </div>
    </div>
  );
}
