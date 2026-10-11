import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api } from "@/api/client";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string | null;
  role_id: string | null;
  is_superuser: boolean;
  is_active: boolean;
  is_email_verified: boolean;
  last_login_at: string | null;
  created_at: string;
  person_ref: string | null;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, full_name: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");
    if (storedToken) {
      setToken(storedToken);
      api
        .get<User>("/auth/me", storedToken)
        .then(setUser)
        .catch(() => {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          setToken(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  async function login(email: string, password: string) {
    const res = await api.post<{
      access_token: string;
      refresh_token: string;
      expires_in: number;
    }>("/auth/login", { email, password });
    localStorage.setItem("access_token", res.access_token);
    localStorage.setItem("refresh_token", res.refresh_token);
    setToken(res.access_token);
    const userRes = await api.get<User>("/auth/me", res.access_token);
    setUser(userRes);
  }

  async function register(email: string, password: string, full_name: string) {
    const res = await api.post<{
      access_token: string;
      refresh_token: string;
      expires_in: number;
    }>("/auth/register", { email, password, full_name });
    localStorage.setItem("access_token", res.access_token);
    localStorage.setItem("refresh_token", res.refresh_token);
    setToken(res.access_token);
    const userRes = await api.get<User>("/auth/me", res.access_token);
    setUser(userRes);
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setToken(null);
    setUser(null);
  }

  async function refreshToken() {
    const storedRefresh = localStorage.getItem("refresh_token");
    if (!storedRefresh) throw new Error("No refresh token");
    const res = await api.post<{
      access_token: string;
      refresh_token: string;
      expires_in: number;
    }>("/auth/refresh", { refresh_token: storedRefresh });
    localStorage.setItem("access_token", res.access_token);
    localStorage.setItem("refresh_token", res.refresh_token);
    setToken(res.access_token);
  }

  return (
    <AuthContext.Provider
      value={{ user, token, isLoading, login, register, logout, refreshToken }}
    >
      {children}
    </AuthContext.Provider>
  );
}
