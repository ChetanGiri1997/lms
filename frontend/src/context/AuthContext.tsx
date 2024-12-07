import React, { createContext, useContext, useState, useEffect } from "react";
import api from "../utils/api";
import {jwtDecode} from "jwt-decode";

interface User {
  id: string;
  role: string;
  sub: string; // For subject claim in JWT
  exp: number; // Expiration time in seconds
  profile_picture?: string;
}

interface AuthContextType {
  user: User | null;
  login: (identifier: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeSession = async () => {
      try {
        const token = localStorage.getItem("token");
        if (token) {
          const decoded: User = jwtDecode<User>(token);

          // Check if token is expired
          if (decoded.exp * 1000 > Date.now()) {
            const role = localStorage.getItem("role") || "";
            const id = localStorage.getItem("id") || "";
            const profile_picture = localStorage.getItem("profile_picture") || "";

            // Set user state
            setUser({ ...decoded, role, id, profile_picture });
          } else {
            console.warn("Token has expired");
            clearLocalStorage();
          }
        }
      } catch (error) {
        console.error("Error initializing session:", error);
        clearLocalStorage();
      } finally {
        setLoading(false);
      }
    };

    initializeSession();
  }, []);

  const login = async (identifier: string, password: string): Promise<boolean> => {
    try {
      const response = await api.post("/login", { identifier, password });
      const { access_token, role, id, profile_picture } = response.data;

      // Store token and additional user info in localStorage
      localStorage.setItem("token", access_token);
      localStorage.setItem("role", role);
      localStorage.setItem("id", id);
      if (profile_picture) {
        localStorage.setItem("profile_picture", profile_picture);
      }

      // Decode and set user data
      const decoded: User = jwtDecode<User>(access_token);
      setUser({ ...decoded, role, id, profile_picture });

      return true;
    } catch (error) {
      console.error("Login failed:", error);
      return false;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await api.post("/logout");
    } catch (error) {
      console.error("Error during logout:", error);
    } finally {
      clearLocalStorage();
      setUser(null);
    }
  };

  const clearLocalStorage = (): void => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("id");
    localStorage.removeItem("profile_picture");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {!loading ? children : <div>Loading...</div>} {/* Replace with a spinner if needed */}
    </AuthContext.Provider>
  );
};
