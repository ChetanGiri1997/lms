import React, { useState, useEffect } from "react";
import api from "../utils/api"; // Your API utility for making requests
import { useAuth } from "../context/AuthContext"; // Assuming you have an AuthContext to get the logged-in user

const ProfileManagement: React.FC = () => {
  const { user } = useAuth();
  const [username, setUsername] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [profilePicture, setProfilePicture] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState<boolean>(false);

  // Fetch user data when component mounts
  useEffect(() => {
    const fetchUserData = async () => {
      if (!user) return;
      try {
        // Replace '/users/{userId}' with the correct endpoint to get the user profile
        const response = await api.get(`/users/${user.id}/profile`);

        if (response.status === 200) {
          const userData = response.data;
          setUsername(userData.username);
          setEmail(userData.email);
          setFirstName(userData.first_name);
          setLastName(userData.last_name);
          if (userData.profile_picture) {
            // Ensure that the profile picture URL is properly formatted
            setImagePreview(
              `${api.defaults.baseURL}/${userData.profile_picture.replace(
                /\\/g,
                "/"
              )}`
            );
          }
        } else {
          console.error("Failed to fetch user data");
        }
      } catch (error) {
        console.error("Error fetching user data:", error);
      }
    };

    if (user?.id) {
      fetchUserData();
    }
  }, [user?.id]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const file = e.target.files[0];
      setProfilePicture(file);

      // Create a preview of the image
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSave = async () => {
    if (!user) {
      console.error("User is not authenticated");
      return;
    }

    const formData = new FormData();
    if (profilePicture) {
      formData.append("profile_picture", profilePicture);
    }

    // Include other user data
    formData.append("username", username);
    formData.append("email", email);
    formData.append("first_name", firstName);
    formData.append("last_name", lastName);

    try {
      const response = await api.put(`/users/${user.id}/profile`, formData); // Assuming PUT is used to update the user data
      if (response.status === 200) {
        alert("Profile updated successfully");
        setIsEditing(false);
      } else {
        console.error("Failed to update profile");
      }
    } catch (error) {
      console.error("Error updating profile:", error);
    }
  };

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg p-6">
      <h2 className="text-2xl font-semibold mb-4">Profile Management</h2>
      <div className="grid grid-cols-1 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Profile Picture
          </label>
          <div className="flex items-center mb-2">
            {imagePreview ? (
              <img
                src={imagePreview}
                alt="Profile Preview"
                className="w-20 h-20 rounded-full mr-4"
              />
            ) : (
              <div className="w-20 h-20 bg-gray-200 rounded-full mr-4"></div>
            )}
            {isEditing && (
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="mt-1 border border-gray-300 rounded-md p-2"
              />
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Username
          </label>
          {isEditing ? (
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 border border-gray-300 rounded-md p-2 w-full"
            />
          ) : (
            <p className="mt-1 text-gray-600">{username}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Email
          </label>
          {isEditing ? (
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 border border-gray-300 rounded-md p-2 w-full"
            />
          ) : (
            <p className="mt-1 text-gray-600">{email}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            First Name
          </label>
          {isEditing ? (
            <input
              type="text"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              className="mt-1 border border-gray-300 rounded-md p-2 w-full"
            />
          ) : (
            <p className="mt-1 text-gray-600">{firstName}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Last Name
          </label>
          {isEditing ? (
            <input
              type="text"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              className="mt-1 border border-gray-300 rounded-md p-2 w-full"
            />
          ) : (
            <p className="mt-1 text-gray-600">{lastName}</p>
          )}
        </div>

        <div className="mt-4">
          {isEditing ? (
            <button
              onClick={handleSave}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Save
            </button>
          ) : (
            <button
              onClick={() => setIsEditing(true)}
              className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
            >
              Edit Profile
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfileManagement;
