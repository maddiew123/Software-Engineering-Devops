import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

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
    fetch("http://localhost:8000/me", {
      credentials: "include", // ✅ send the secure cookie
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