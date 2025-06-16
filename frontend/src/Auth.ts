

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

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
        const res = await fetch(`${API_BASE_URL}/me`, {
          credentials: "include", 
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

export const logout = async () => {
  try {
    await fetch(`${API_BASE_URL}/logout`, {
      method: "POST",
      credentials: "include",
    });
  } catch (err) {
    console.error("Logout failed", err);
  }
};
