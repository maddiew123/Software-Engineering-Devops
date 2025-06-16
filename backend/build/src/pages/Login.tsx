import axios from "axios";
import { useNavigate } from "react-router";
// import { fetchToken, setToken } from "./Auth";
import { useState } from "react";
import "../styling/Login.css"
import HeaderComponent from "../components/HeaderComponent";


export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");


  const login = () => {
    if ((username == "") && (password == "")) {
      console.log("poop")
      return;
    } else {
      console.log("hello")
      axios
        .post("http://localhost:8000/login", {
          username: username,
          password_hash: password,
        },
      {
        withCredentials: true, // ✅ This sends and receives HTTP-only cookies
      })
        .then(function (response) {
          console.log(response.data.message, "response.data.token");
          if (response.data.message === "login_success") {
      navigate("/profile");
    } else {
      alert("Login failed");
    }
        })
        .catch(function (error) {
          console.log(error, "error");
        });
    }
  };

  return (
    <div className="background">
    <HeaderComponent admin={false}loggedIn={false} />
      <div className="wrapper">
       
      <div className="box">
       
 
        
      <h1 className="title">Login Page</h1>
         
      <>
      <p>username</p>
      <input
                  type="text"
                  onChange={(e) => setUsername(e.target.value)}
                  
                />
      <p>password</p>
      <input
                  type="password"
                  onChange={(e) => setPassword(e.target.value)}
                />
      <button type="button" onClick={login}>
                  Login
                </button>
      </>

    </div>
                <p className="signUp" onClick={()=>navigate("/signup")}>Sign Up</p>
     
     </div>
    </div>
   
   
  
  );
}
