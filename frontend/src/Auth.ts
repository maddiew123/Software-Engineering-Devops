// import type { ReactNode } from "react"
// import { useNavigate } from "react-router-dom"

// export const setToken = (token : string)=>{

//     localStorage.setItem('tokenya', token)
// }

// export const fetchToken = ()=>{
//     localStorage.removeItem("tokenya")

//     return localStorage.getItem('tokenya')
// }
// export const setCurrentUser = (current_user : string) =>{
//     localStorage.setItem('userya', current_user)
// }
// export const fetchCurrentUser = () =>{
//     localStorage.getItem('userya')
// }

// export function RequireToken({children}: {children: ReactNode}){

//     let auth = fetchToken()
//     let navigate = useNavigate()

//     if(!auth){

//         navigate("/");
//     } else {
//         navigate("/profile");
//     }

//     return children;
// }

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

// Utility hook to check if the user is authenticated
export function useAuth() {
  const [user, setUser] = useState<null | {
    username: string;
    role: string;
    team_id: string;
  }>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetch("http://localhost:8000/me", {
          credentials: "include", // <-- include cookies
        });

        if (res.ok) {
          const data = await res.json();
          setUser(data);
        } else {
          setUser(null);
          navigate("/");
        }
      } catch (err) {
        console.error("Auth check failed", err);
        setUser(null);
        navigate("/");
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [navigate]);

  return { user, loading };
}

// Optional helper to logout
export const logout = async () => {
  try {
    await fetch("http://localhost:8000/logout", {
      method: "POST",
      credentials: "include",
    });
  } catch (err) {
    console.error("Logout failed", err);
  }
};
