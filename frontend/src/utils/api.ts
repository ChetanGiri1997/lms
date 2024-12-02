import axios from "axios";

// Create an Axios instance
const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api/", // Replace with your API URL
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

      
      window.location.href = "/login"; // Redirect to the login page

      // Optionally, you can clear the localStorage token here if needed:
      localStorage.removeItem("token");
    }
    return Promise.reject(error);
  }
);

export default api;
