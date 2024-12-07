import axios from "axios";

// Create an Axios instance
const api = axios.create({
  baseURL: "https://api.chetangiri.com.np/api/", // Replace with your API URL
});

// Request Interceptor
api.interceptors.request.use(
  (config) => {
    // Add the Authorization token if it exists in localStorage
    const token = localStorage.getItem("token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor
// Response Interceptor
api.interceptors.response.use(
  (response) => {
    // Return the response if no error occurs
    return response;
  },
  (error) => {
    // If the error response is 401 (Unauthorized), redirect to the login page
    if (error.response && error.response.status === 401) {
      // Log the error or perform any other necessary actions
      console.error("Unauthorized, redirecting to login...");
      
      // Clear all authentication-related items
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      localStorage.removeItem("id");
      localStorage.removeItem("profile_picture");
      
      window.location.href = "/login"; // Redirect to the login page
    }
    return Promise.reject(error);
  }
);

export default api;
