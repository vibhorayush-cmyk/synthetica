"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { currentUser, login, logout, register } from "@/services/auth-service";
import { getAccessToken } from "@/services/api-client";
import type { User } from "@/types/auth";

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (fullName: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const refreshUser = async () => {
    if (!getAccessToken()) { setUser(null); setLoading(false); return; }
    try { setUser(await currentUser()); } catch { setUser(null); }
    finally { setLoading(false); }
  };
  useEffect(() => { void refreshUser(); }, []);
  const value = useMemo(() => ({
    user,
    loading,
    refreshUser,
    login: async (email: string, password: string) => { await login(email, password); await refreshUser(); },
    register: async (fullName: string, email: string, password: string) => { setUser(await register(fullName, email, password)); setLoading(false); },
    logout: async () => { await logout(); setUser(null); },
  }), [user, loading]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
