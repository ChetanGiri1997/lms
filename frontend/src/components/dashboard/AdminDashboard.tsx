import React, { useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from '../Sidebar';
import UserManagement from '../UserManagement';
import ProfileManagement from '../ProfileManagement';
import Information from '../Information';
import { Menu } from 'lucide-react';  // Icon for mobile sidebar toggle
import { useAuth } from '../../context/AuthContext';
import Courses from '../Course/CourseList';
import CourseForm from '../Course/CourseForm';

const AdminDashboard: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // Sidebar toggle state

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Sidebar for desktop and toggleable for mobile */}
      <div className={`${isSidebarOpen ? 'block' : 'hidden'} lg:block`}>
        <Sidebar role="admin" />
      </div>

      <div className="flex-1">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>

            {/* Hamburger menu for mobile sidebar toggle */}
            <button
              className="lg:hidden text-gray-900 p-2 rounded-md focus:outline-none focus:ring-2 focus:ring-inset focus:ring-gray-600"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            >
              <Menu size={24} />
            </button>
          </div>
        </header>

        <main className="p-4">
          <Routes>
            {/* Redirect to info if the user visits /dashboard */}
            <Route path="/" element={<Navigate to="info" replace />} />

            {/* Admin-specific routes */}
            <Route path="users" element={<UserManagement />} />
            <Route path="profile" element={<ProfileManagement />} />
            <Route path="info" element={<Information />} /> {/* Default info page */}

            <Route path="courses/list" element={<Courses  />} />
            <Route path="courses/add" element={<CourseForm onClose={() => {}} />} />

          </Routes>
        </main>
      </div>
    </div>
  );
};

export default AdminDashboard;
