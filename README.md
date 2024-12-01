# 🎓 **Learning Management System (LMS)** - FARM Stack

Welcome to the **Learning Management System (LMS)** built with the powerful **FARM stack** (FastAPI, React, MongoDB, and MongoDB). This system is designed to help educators manage courses, students, and resources efficiently, with a modern front-end interface and a robust back-end API.

---

## 🌟 **Features**

- **Authentication & Authorization**: Secure user login and JWT-based token authentication.
- **Course Management**: Create, update, and manage courses.
- **User Management With RBAC**: Admins can manage users, assign roles (students, instructors, etc.).
- **Student Dashboard**: Personalized dashboard for students to view and track their enrolled courses.
- **Real-Time Notifications**: Push notifications to inform users of important events.
- **Media Storage**: Support for file uploads like course materials and profile pictures.
- **RESTful API**: Built with FastAPI for fast, async, and scalable interactions.

---

## 🛠️ **Tech Stack**

- **Frontend**:  
  - **React** - A fast, efficient, and flexible JavaScript library for building user interfaces.
  - **Axios** - Promise-based HTTP client for making API requests.
  - **Material-UI** - React UI framework for modern, responsive design.

- **Backend**:  
  - **FastAPI** - A modern, fast (high-performance) web framework for building APIs with Python.
  - **JWT Authentication** - Secure login with JSON Web Tokens.
  - **Pydantic** - Data validation and settings management using Python type annotations.
  - **MongoDB** - NoSQL database for storing user, course, and session data.

- **Deployment**:  
  - **Docker** - For containerization of the application.
  - **Nginx** - Reverse proxy server for handling requests and serving static files.

---

## 📸 **Screenshots**

### Login Page:
![Login Page](https://via.placeholder.com/800x400.png?text=Login+Page)

### Dashboard:
![Student Dashboard](https://via.placeholder.com/800x400.png?text=Student+Dashboard)

### Course Management:
![Course Management](https://via.placeholder.com/800x400.png?text=Course+Management)

---

## 🚀 **Quick Start Guide**

Follow these steps to get your LMS up and running locally!

### **1. Clone the Repository**


git clone https://github.com/yourusername/lms-farm-stack.git
cd lms-farm-stack

### 2. Set up the Backend (FastAPI + MongoDB)
Requirements:
Python 3.8+
MongoDB instance (either local or use a service like MongoDB Atlas)
Docker (Optional but recommended for deployment)

Install Backend Dependencies:

cd backend
pip install -r requirements.txt
Create a .env file:
In the backend folder, create a .env file with the following variables:

MONGODB_URL=mongodb://localhost:27017
DB_NAME=lms_db
ACCESS_TOKEN_EXPIRY=30
SECRET_KEY=your_secret_key_here
Run Backend Server:
bash
Copy code
uvicorn main:app --reload
This will start the FastAPI server on http://localhost:8000.

### 3. Set up the Frontend (React)
Install Frontend Dependencies:

cd frontend
npm install
Run the React Development Server:
bash
Copy code
npm start
This will start the React app on http://localhost:3000.

### 4. Running Everything with Docker (Optional)
If you prefer to run the full application in containers, you can use Docker Compose.

Build and Run Containers:

docker-compose up --build
This will set up both the backend and frontend along with the MongoDB database in isolated containers.

## 📱 API Endpoints
The following API endpoints are available:

Authentication
POST /token
Get JWT token by providing username and password.
Example body:


{
  "username": "chetan",
  "password": "password123"
}

POST /api/logout
Invalidate the current user’s JWT token.

User Management
GET /api/users
Fetch all users (Admin only).

POST /api/users
Create a new user (Admin only).

PUT /api/users/{user_id}
Update a user’s details (Admin only).

DELETE /api/users/{user_id}
Delete a user (Admin only).

Course Management
GET /api/courses
Fetch all courses.

POST /api/courses
Create a new course (Instructor/Admin only).

PUT /api/courses/{course_id}
Update course details (Instructor/Admin only).

DELETE /api/courses/{course_id}
Delete a course (Instructor/Admin only).

Student Dashboard
GET /api/student/courses
Fetch all courses a student is enrolled in.

## 🔒 Security
This project uses JWT (JSON Web Token) authentication to secure all routes that require authorization. Ensure that you pass the Bearer token obtained from the /token endpoint in the Authorization header of the request.

## 🎉 Contributing
We welcome contributions to improve the system! If you want to contribute, follow these steps:

Fork the repository.
Create a feature branch: git checkout -b feature-branch.
Make your changes.
Commit your changes: git commit -m 'Add feature'.
Push to your forked repository: git push origin feature-branch.
Open a pull request.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 💬 Contact
If you have any questions or need help, feel free to reach out:

Email: info@chetangiri.com.np
GitHub: https://github.com/ChetanGiri1997

## 👨‍🏫 Learning Resources
For those who want to learn more about the technologies used in this LMS:

FastAPI Documentation: https://fastapi.tiangolo.com
React Documentation: https://reactjs.org/docs/getting-started.html
MongoDB Documentation: https://docs.mongodb.com

## 📦 Future Enhancements
Adding video conferencing for virtual classes.
Improved reporting and analytics for admins.
Real-time messaging/chat between students and instructors.
Integration with third-party tools like Google Classroom or Zoom.


# Thank you for checking out this project! 🚀
