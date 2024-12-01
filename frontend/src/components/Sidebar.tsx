import React, { useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import {
  LogOut,
  Users,
  Book,
  GraduationCap,
  User,
  ChevronDown,
  ChevronUp,
  PlusCircle,
  List,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface SidebarProps {
  role: 'admin' | 'teacher' | 'student';
}

const Sidebar: React.FC<SidebarProps> = ({ role }) => {
  const { user, logout } = useAuth();

  // Redirect to login if user is not authenticated
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const [isCoursesMenuOpen, setIsCoursesMenuOpen] = useState(false); // State to manage course submenu

  // Toggle course submenu
  const toggleCoursesMenu = () => {
    setIsCoursesMenuOpen((prev) => !prev);
  };

  return (
    <div className="bg-gray-800 text-white w-64 md:w-72 lg:w-80 p-4 overflow-y-auto h-full fixed lg:relative lg:min-h-screen">
      <div className="flex items-center space-x-4 mb-6">
        <img
          src={user.photoUrl} // Assuming the `photoUrl` is part of the `user` object
          alt="User Profile"
          className="w-12 h-12 rounded-full object-cover"
        />
        <div>
          <p className="text-lg font-semibold">{user.name || 'User'}</p>
          <p className="text-sm text-gray-400">{user.email}</p>
        </div>
      </div>
      <h2 className="text-2xl font-semibold mb-6">
        {role.charAt(0).toUpperCase() + role.slice(1)} Dashboard
      </h2>
      <nav>
        <ul className="space-y-2">
          {/* User Management visible to admins and teachers */}
          {(role === 'admin' || role === 'teacher') && (
            <li>
              <Link to="/dashboard/users" className="flex items-center space-x-2 p-2 rounded hover:bg-gray-700">
                <Users size={20} />
                <span>User Management</span>
              </Link>
            </li>
          )}

          {/* Course management for teachers and students */}
          <li>
            <button
              onClick={toggleCoursesMenu}
              className="flex items-center space-x-2 p-2 rounded hover:bg-gray-700 w-full text-left"
            >
              {role === 'teacher' ? <Book size={20} /> : <GraduationCap size={20} />}
              <span>{role === 'teacher' ? 'Course Management' : 'Courses'}</span>
              {isCoursesMenuOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </button>

            {/* Submenu for courses */}
            {isCoursesMenuOpen && (
              <ul className="ml-6 space-y-2">
                {/* Course List available to all roles */}
                <li>
                  <Link to="/dashboard/courses/list" className="flex items-center space-x-2 p-2 rounded hover:bg-gray-700">
                    <List size={20} />
                    <span>Course List</span>
                  </Link>
                </li>

                {/* Add Course visible to admins and teachers */}
                {(role === 'admin' || role === 'teacher') && (
                  <li>
                    <Link to="/dashboard/courses/add" className="flex items-center space-x-2 p-2 rounded hover:bg-gray-700">
                      <PlusCircle size={20} />
                      <span>Add Course</span>
                    </Link>
                  </li>
                )}
              </ul>
            )}
          </li>

          {/* Profile section available for all roles */}
          <li>
            <Link to="/dashboard/profile" className="flex items-center space-x-2 p-2 rounded hover:bg-gray-700">
              <User size={20} />
              <span>Profile</span>
            </Link>
          </li>

          {/* Logout button available for all roles */}
          <li>
            <button onClick={logout} className="flex items-center space-x-2 p-2 rounded hover:bg-gray-700 w-full text-left">
              <LogOut size={20} />
              <span>Logout</span>
            </button>
          </li>
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;
