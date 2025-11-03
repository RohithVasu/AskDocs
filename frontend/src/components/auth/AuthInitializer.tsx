// src/components/auth/AuthInitializer.tsx
import { useEffect } from "react";
import { useAuthStore } from "@/stores/authStore";
import api from "@/lib/api";

export const AuthInitializer = () => {
  const { user, setUser, logout } = useAuthStore();

  useEffect(() => {
    const loadUser = async () => {
      try {
        const token = localStorage.getItem("access_token");
        if (token && !user) {
          const res = await api.get("/auth/me", {
            headers: { Authorization: `Bearer ${token}` },
          });
          const data = res.data.data;
          setUser({
            id: data.id,
            email: data.email,
            first_name: data.firstname,
            last_name: data.lastname,
          });
        }
      } catch {
        logout(); // Invalid or expired token
      }
    };
    loadUser();
  }, [user, setUser, logout]);

  return null; // Invisible component
};
