import {
  createContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { useNavigate } from "react-router-dom";

import { authApi } from "../api/auth";
import { isUnauthenticatedError } from "../api/client";
import type { AuthUser } from "../api/types";

type LoginInput = {
  username: string;
  password: string;
};

type AuthContextValue = {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (input: LoginInput) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function refreshSession() {
    try {
      const response = await authApi.me();
      setUser(response.user);
    } catch (error) {
      if (!isUnauthenticatedError(error)) {
        console.error(error);
      }
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }

  async function login(input: LoginInput) {
    const response = await authApi.login(input);
    setUser(response.user);
    navigate("/links/search", { replace: true });
  }

  async function logout() {
    try {
      await authApi.logout();
    } finally {
      setUser(null);
      navigate("/login", { replace: true });
    }
  }

  useEffect(() => {
    void refreshSession();
  }, []);

  const value: AuthContextValue = {
    user,
    isAuthenticated: user !== null,
    isLoading,
    login,
    logout,
    refreshSession,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
