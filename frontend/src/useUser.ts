import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL|| "http://127.0.0.1:8000";
type User = {
  username: string;
  full_name: string;
  team_id: string;
  role: string;
};

export function useUser() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`${API_BASE_URL}/me`, {
      credentials: "include", 
    })
      .then(async (res) => {
        if (!res.ok) throw new Error("Not logged in");
        const data = await res.json();
        setUser(data);
      })
      .catch(() => {
        navigate("/");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [navigate]);

  return { user, loading };
}