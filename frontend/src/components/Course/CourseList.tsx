import React, { useEffect, useState } from 'react';
import api from '../../utils/api'; // Using api from the api.ts file

// Define the Course and Teacher types
interface Teacher {
  id: string;
  name: string;
  email?: string;
}

interface Course {
  id: string;
  name: string;
  description: string;
  teachers?: Teacher[];
}

// Component for listing all available courses
const CourseList: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]); // Courses state
  const [loading, setLoading] = useState<boolean>(true); // Loading state
  const [error, setError] = useState<string | null>(null); // Error state
  const [currentPage, setCurrentPage] = useState<number>(1); // Current page for pagination
  const [totalPages, setTotalPages] = useState<number>(1); // Total pages for pagination
  

  // Fetch courses with pagination
  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true);
        const response = await api.get('/courses');
        setCourses(response.data.courses); // Assuming API returns { courses, totalPages }
        setTotalPages(response.data.totalPages);
        setLoading(false);
      } catch (err) {
        setError((err as Error).message);
        setLoading(false);
      }
    };
    fetchCourses();
  }, [currentPage]);

  // Handle page change
  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  if (loading) return <div>Loading courses...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Courses</h1>

      {/* Course Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {courses.map((course) => (
          <div key={course.id} className="bg-white p-4 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold">{course.name}</h2>
            <p className="text-gray-600 mt-2">{course.description}</p>
            {course.teachers && course.teachers.length > 0 && (
              <p className="text-sm text-gray-500 mt-4">
                Instructor: {course.teachers.map((teacher) => teacher.name).join(', ')}
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Pagination Controls */}
      <div className="mt-6 flex justify-center space-x-2">
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50"
        >
          Previous
        </button>
        <span className="px-4 py-2">{currentPage} of {totalPages}</span>
        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default CourseList;
