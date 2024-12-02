import React, { useState, useEffect } from "react";
import { Navigate } from "react-router-dom";
import api from "../utils/api";
import { useAuth } from "../context/AuthContext";

interface UserFormProps {
  userId?: string | undefined | null; // Optional: for editing
  onClose: () => void; // Function to close the form
}

const UserForm: React.FC<UserFormProps> = ({ userId, onClose }) => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const [username, setUsername] = useState<string>("");
  const [role, setRole] = useState<string>("student"); // Default role
  const [email, setEmail] = useState<string>("");
  const [first_name, setfirst_name] = useState<string>("");
  const [last_name, setlast_name] = useState<string>("");
  const [password, setPassword] = useState<string>(""); // Password state
  const [repeatPassword, setRepeatPassword] = useState<string>(""); // New repeat password state
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [passwordStrength, setPasswordStrength] = useState<string>("");
  const [passwordsMatch, setPasswordsMatch] = useState<boolean>(true);

  useEffect(() => {
    if (userId) {
      const fetchUser = async () => {
        try {
          const response = await api.get(`/edit_users/${userId}`); // Change to GET for fetching user data
          const userData = response.data;
          setUsername(userData.username);
          setRole(userData.role);
          setEmail(userData.email);
          setfirst_name(userData.first_name);
          setlast_name(userData.last_name);
          setIsEditing(true);
        } catch (error) {
          console.error("Error fetching user:", error);
        }
      };
      fetchUser();
    }
  }, [userId]);

  const validatePassword = (password: string) => {
    const lengthValid = password.length >= 8;
    const numberValid = /[0-9]/.test(password);
    const uppercaseValid = /[A-Z]/.test(password);
    const lowercaseValid = /[a-z]/.test(password);
    const specialCharValid = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    if (
      lengthValid &&
      numberValid &&
      uppercaseValid &&
      lowercaseValid &&
      specialCharValid
    ) {
      setPasswordStrength("Strong");
    } else if (
      lengthValid &&
      (numberValid || uppercaseValid || lowercaseValid)
    ) {
      setPasswordStrength("Moderate");
    } else {
      setPasswordStrength("Weak");
    }
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    validatePassword(newPassword);
    setPasswordsMatch(newPassword === repeatPassword);
  };

  const handleRepeatPasswordChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const newRepeatPassword = e.target.value;
    setRepeatPassword(newRepeatPassword);
    setPasswordsMatch(newRepeatPassword === password);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const userData: {
        username: string;
        role: string;
        email: string;
        first_name: string;
        last_name: string;
        password?: string; // Optional, only for new users
      } = { username, role, email, first_name, last_name };

      if (!isEditing) {
        userData.password = password; // Include password only for new users
      }

      if (isEditing) {
        // Update user

        await api.put(`/edit_users/${userId}`, userData);
      } else {
        // Add new user

        await api.post("/register", userData);
      }
      onClose(); // Close the form after success
    } catch (error) {
      console.error("Error saving user:", error);
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white p-6 rounded shadow-md w-full max-w-lg h-full max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl mb-4">
          {isEditing ? "Edit User" : "Add User"}
        </h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="mt-1 block w-full border border-gray-300 rounded-md p-2"
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 block w-full border border-gray-300 rounded-md p-2"
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">
              First Name
            </label>
            <input
              type="text"
              value={first_name}
              onChange={(e) => setfirst_name(e.target.value)}
              required
              className="mt-1 block w-full border border-gray-300 rounded-md p-2"
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">
              Last Name
            </label>
            <input
              type="text"
              value={last_name}
              onChange={(e) => setlast_name(e.target.value)}
              required
              className="mt-1 block w-full border border-gray-300 rounded-md p-2"
            />
          </div>
          {!isEditing && ( // Only show password fields when not editing
            <>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={handlePasswordChange}
                  required={!isEditing} // Require password only for new users
                  className="mt-1 block w-full border border-gray-300 rounded-md p-2"
                />
                {password && (
                  <div
                    className={`text-sm ${
                      passwordStrength === "Strong"
                        ? "text-green-600"
                        : passwordStrength === "Moderate"
                        ? "text-yellow-600"
                        : "text-red-600"
                    }`}
                  >
                    Password Strength: {passwordStrength}
                  </div>
                )}
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">
                  Repeat Password
                </label>
                <input
                  type="password"
                  value={repeatPassword}
                  onChange={handleRepeatPasswordChange}
                  required={!isEditing} // Require repeat password only for new users
                  className={`mt-1 block w-full border ${
                    passwordsMatch ? "border-gray-300" : "border-red-600"
                  } rounded-md p-2`}
                />
                {!passwordsMatch && repeatPassword && (
                  <div className="text-red-600 text-sm">
                    Passwords do not match
                  </div>
                )}
              </div>
            </>
          )}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">
              Role
            </label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              disabled={user.role === "teacher"} // Disable if the current user is a teacher
              className="mt-1 block w-full border border-gray-300 rounded-md p-2"
            >
              <option value="student">Student</option>
              <option value="teacher">Teacher</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div className="flex justify-end">
            <button
              type="button"
              onClick={onClose}
              className="mr-2 px-4 py-2 bg-gray-300 rounded"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded"
            >
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UserForm;
