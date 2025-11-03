// src/stores/authStore.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";
import { User } from "@/types";
import api from "@/lib/api";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  logout: () => void;
  fetchUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: !!localStorage.getItem("access_token"),

      setUser: (user) => set({ user, isAuthenticated: !!user }),

      logout: () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        set({ user: null, isAuthenticated: false });
      },

      // ✅ Fetch current user from backend
      fetchUser: async () => {
        try {
          const token = localStorage.getItem('access_token')
          if (!token) return;
          const userResponse = await api.get('/auth/me', {
            headers: { Authorization: `Bearer ${token}` },
          });
          const userData = userResponse.data.data;
          const user: User = {
            id: userData.id,
            email: userData.email,
            first_name: userData.firstname,
            last_name: userData.lastname,
          };
          set({ user, isAuthenticated: true });
        } catch (err) {
          console.error("Failed to fetch user:", err);
          set({ user: null, isAuthenticated: false });
        }
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
