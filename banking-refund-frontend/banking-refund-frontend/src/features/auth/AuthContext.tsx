import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import api from "../../lib/api";
import type { AuthResponse, User } from "../../types";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<User>;
  signup: (name: string, email: string, password: string) => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function persist(auth: AuthResponse) {
  localStorage.setItem("refund_access_token", auth.access_token);
  localStorage.setItem("refund_user", JSON.stringify(auth.user));
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState(localStorage.getItem("refund_access_token"));
  const [user, setUser] = useState<User | null>(() => {
    const raw = localStorage.getItem("refund_user");
    return raw ? JSON.parse(raw) : null;
  });

  const login = async (email: string, password: string) => {
    const { data } = await api.post<AuthResponse>("/auth/login", { email, password });
    persist(data);
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  };

  const signup = async (name: string, email: string, password: string) => {
    const { data } = await api.post<AuthResponse>("/auth/signup", { name, email, password });
    persist(data);
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  };

  const logout = () => {
    localStorage.removeItem("refund_access_token");
    localStorage.removeItem("refund_user");
    setToken(null);
    setUser(null);
  };

  const value = useMemo(() => ({ user, token, login, signup, logout }), [user, token]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
