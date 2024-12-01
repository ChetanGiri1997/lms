import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from '../Sidebar';
import Information from '../Information';
import ProfileManagement from '../ProfileManagement';
import { useAuth } from '../../context/AuthContext';
import UserManagement from '../UserManagement';

const TeacherDashboard: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  };
 



  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar role="teacher" />
      <div className="flex-1">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold text-gray-900">Teacher Dashboard</h1>
          </div>
        </header>
        <Routes>
          {/* Redirect to info if the user visits /dashboard */}
          <Route path="/" element={<Navigate to="info" replace />} />
          <Route path="/profile" element={<ProfileManagement />} />
          <Route path="/info" element={<Information />} />
          <Route path="/users" element={<UserManagement />} />
        </Routes>
      </div>
    </div>
  );
};

export default TeacherDashboard;
