import React from 'react';

const Information: React.FC = () => {
  return (
    
    <div className="container mx-auto p-8 bg-white shadow-lg rounded-lg">
      <h1 className="text-3xl font-bold text-center mb-6">Welcome to the Dashboard</h1>
      <p className="text-center text-lg text-gray-700 mb-8">
        This is a simple landing page for the dashboard. You can find key information and links to various sections here.
      </p>

      <div className="flex justify-around mb-10">
        <section className="w-1/3 p-4 bg-blue-50 rounded-lg shadow">
          <h2 className="text-2xl font-semibold text-blue-600 mb-4">Overview</h2>
          <p className="text-gray-700">Get an overview of your account activities, recent updates, and notifications.</p>
        </section>
        <section className="w-1/3 p-4 bg-green-50 rounded-lg shadow">
          <h2 className="text-2xl font-semibold text-green-600 mb-4">Courses</h2>
          <p className="text-gray-700">Access your courses, view details, and track your progress.</p>
        </section>
        <section className="w-1/3 p-4 bg-yellow-50 rounded-lg shadow">
          <h2 className="text-2xl font-semibold text-yellow-600 mb-4">Profile</h2>
          <p className="text-gray-700">Manage your profile settings and update your personal information.</p>
        </section>
      </div>

      <footer className="text-center text-gray-600 text-sm">
        <p>© 2024 Your LMS Platform. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default Information;
