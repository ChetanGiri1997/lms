// src/routes/Routes.tsx
import React from 'react';
import { 
  Navigate, 
  Outlet, 
  Route, 
  Routes as ReactRoutes 
} from 'react-router-dom';
import PrivateRoute from './components/auth/PrivateRoute';

// Dashboard Components
import AdminDashboard from './components/dashboard/AdminDashboard';
import StudentDashboard from './components/dashboard/StudentDashboard';
import TeacherDashboard from './components/dashboard/TeacherDashboard';

// Auth Components
import Login from './components/auth/Login';

// Course Components
import CourseList from './components/Course/CourseList';
import CourseDetail from './components/Course/CourseDetail';
import CourseForm from './components/Course/CourseForm';

// Assignment Components
import AssignmentList from './components/Assignments/AssignmentList';
import AssignmentDetail from './components/Assignments/AssignmentDetail';
import AssignmentForm from './components/Assignments/AssignmentForm';

// Lesson Components
import LessonList from './components/Materials/MaterialList';
import LessonDetail from './components/Materials/StudyMaterial';
import LessonForm from './components/Materials/MaterialForm';

// User Management
import UserManagement from './components/UserManagement';
import ProfileManagement from './components/ProfileManagement';

// Hooks and Context
import { useAuth } from './context/AuthContext';

// Role-based route protection
const RoleBasedRoute: React.FC<{
  allowedRoles: string[];
  children: React.ReactNode;
}> = ({ allowedRoles, children }) => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

// Unauthorized Page
const Unauthorized = () => (
  <div className="flex items-center justify-center h-screen">
    <h1 className="text-2xl text-red-500">Unauthorized Access</h1>
  </div>
);

const Routes: React.FC = () => {
  return (
    <ReactRoutes>
      {/* Public Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/unauthorized" element={<Unauthorized />} />

      {/* Protected Routes with Layout */}
      <Route 
        element={
          <PrivateRoute>
            <Outlet />
          </PrivateRoute>
        }
      >
        {/* Common Routes for All Authenticated Users */}
        <Route path="/profile" element={<ProfileManagement />} />

        {/* Admin-specific Routes */}
        <Route 
          path="/admin/*" 
          element={
            <RoleBasedRoute allowedRoles={['admin']}>
              <Outlet />
            </RoleBasedRoute>
          }
        >
          <Route index element={<AdminDashboard />} />
          <Route path="users" element={<UserManagement />} />
          <Route path="courses/new" element={<CourseForm />} />
        </Route>

        {/* Teacher-specific Routes */}
        <Route 
          path="/teacher/*" 
          element={
            <RoleBasedRoute allowedRoles={['teacher']}>
              <Outlet />
            </RoleBasedRoute>
          }
        >
          <Route index element={<TeacherDashboard />} />
          <Route path="courses" element={<CourseList />} />
          <Route path="courses/:id" element={<CourseDetail />} />
          <Route path="assignments" element={<AssignmentList />} />
          <Route path="assignments/new" element={<AssignmentForm />} />
          <Route path="lessons/new" element={<LessonForm />} />
        </Route>

        {/* Student-specific Routes */}
        <Route 
          path="/student/*" 
          element={
            <RoleBasedRoute allowedRoles={['student']}>
              <Outlet />
            </RoleBasedRoute>
          }
        >
          <Route index element={<StudentDashboard />} />
          <Route path="courses" element={<CourseList />} />
          <Route path="courses/:id" element={<CourseDetail />} />
          <Route path="assignments" element={<AssignmentList />} />
          <Route path="assignments/:id" element={<AssignmentDetail />} />
        </Route>

        {/* Catch-all redirect based on user role */}
        <Route 
          path="/" 
          element={<Navigate to={`/${user?.role || 'login'}`} replace />} 
        />
      </Route>

      {/* 404 Not Found */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </ReactRoutes>
  );
};

export default Routes;