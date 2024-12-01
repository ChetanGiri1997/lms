import React from 'react';
import { useAuth } from '../context/AuthContext';
import AdminDashboard from './dashboard/AdminDashboard';
import TeacherDashboard from './dashboard/TeacherDashboard';
import StudentDashboard from './dashboard/StudentDashboard';
import { Navigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  switch (user.role) {
    case 'admin':
      return <AdminDashboard />;
    case 'teacher':
      return <TeacherDashboard />;
    case 'student':
      return <StudentDashboard />;
    default:
      return <div>Invalid user role</div>;
  }
};

export default Dashboard;
