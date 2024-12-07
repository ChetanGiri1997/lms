import React from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import Login from "./components/auth/Login";
import Dashboard from "./components/Dashboard";
import CourseDetail from "./components/Course/CourseDetail";
import PrivateRoute from "./components/auth/PrivateRoute";
import { AuthProvider } from "./context/AuthContext";

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Route */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected Routes */}
          <Route element={<PrivateRoute />}>
            {/* User Dashboard */}
            <Route path="/dashboard/*" element={<Dashboard />} />
            
            {/* Course Dashboard */}
            <Route path="/dashboard/courses" element={<CourseDetail />} />
          </Route>
          
          {/* Fallback Route */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
