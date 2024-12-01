import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/api';
import { jwtDecode } from 'jwt-decode';

interface User {
  sub: string;
  role: string;
  exp: number;
  id: string;
  photoUrl: string; // Add photoUrl to the User interface
}

interface AuthContextType {
  user: User | null;
  login: (identifier: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkSession();
  }, []);

  const checkSession = async () => {
    const token = localStorage.getItem('token');
    
    if (token) {
      try {
        const decoded: User = jwtDecode<User>(token);
        // Check if the token is still valid
        if (decoded.exp * 1000 > Date.now()) {
          const role = localStorage.getItem('role') || '';
          const id = localStorage.getItem('id') || '';
          
          setUser({ ...decoded, role, id });
        } else {
          localStorage.removeItem('token');
          setUser(null); // Update user state
        }
      } catch (error) {
        console.error('Error decoding token:', error);
        localStorage.removeItem('token');
        setUser(null); // Update user state
      }
    }
    setLoading(false);
  };
  
  const login = async (identifier: string, password: string) => {
    try {
      const response = await api.post('/login', { identifier, password });
      console.log(response);
      
      const { access_token, role, id, photoUrl } = response.data;  // Ensure photoUrl is in the response
  
      // Store the token, role, id, and photoUrl in local storage
      localStorage.setItem('token', access_token);
      localStorage.setItem('role', role);
      localStorage.setItem('id', id);
      localStorage.setItem('photoUrl', photoUrl); // Store photoUrl as well
  
      // Decode the JWT token and set user data including photoUrl
      const decoded: User = jwtDecode(access_token);
      setUser({ ...decoded, role, id, photoUrl });  // Include photoUrl in the user state
  
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false; // Consider setting an error state to provide feedback
    }
  };
  

  const logout = async () => {
    try {
      await api.post('/logout');
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      localStorage.removeItem('id');
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };
  
  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
