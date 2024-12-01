import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const PrivateRoute: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>; // Or a loading spinner component
  }

  return user ? <Outlet /> : <Navigate to="/login" />;
};

export default PrivateRoute;
