import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../../utils/api';

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
  owner: {
    _id: string;
    name: string;
    role: string;
  };
  archived: boolean;
  enrolled: boolean;
}

const CourseDashboard: React.FC = () => {
  const { id } = useParams<{ id: string }>(); // Extract the course ID from the route params
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch course details
  const fetchCourseDetails = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/courses/${id}`);
      setCourse(response.data.course);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // Effect to fetch course data when the component mounts
  useEffect(() => {
    fetchCourseDetails();
  }, [id]);

  if (loading) return <div>Loading course details...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!course) return <div>No course found.</div>;

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">{course.name}</h1>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-600 mb-4">{course.description}</p>
        <div className="mb-4">
          <h2 className="text-lg font-semibold">Instructor(s):</h2>
          {course.teachers && course.teachers.length > 0 ? (
            <ul>
              {course.teachers.map((teacher) => (
                <li key={teacher.id} className="text-gray-700">
                  {teacher.name} {teacher.email && `(${teacher.email})`}
                </li>
              ))}
            </ul>
          ) : (
            <p>No instructors assigned.</p>
          )}
        </div>
        <div className="mb-4">
          <h2 className="text-lg font-semibold">Course Owner:</h2>
          <p>
            {course.owner.name} - {course.owner.role}
          </p>
        </div>
        <div className="mb-4">
          <h2 className="text-lg font-semibold">Course Status:</h2>
          <p>{course.archived ? 'Archived' : 'Active'}</p>
        </div>
        <div className="flex space-x-4">
          <Link
            to="/courses"
            className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
          >
            Back to Courses
          </Link>
          {!course.archived && (
            <button
              className={`px-4 py-2 rounded-md ${
                course.enrolled
                  ? 'bg-yellow-500 hover:bg-yellow-600 text-white'
                  : 'bg-green-500 hover:bg-green-600 text-white'
              }`}
              onClick={async () => {
                try {
                  if (course.enrolled) {
                    await api.post(`/courses/${id}/optout`);
                  } else {
                    await api.post(`/courses/${id}/enroll`);
                  }
                  fetchCourseDetails(); // Refresh the course details
                } catch (err) {
                  setError((err as Error).message);
                }
              }}
            >
              {course.enrolled ? 'Opt-Out' : 'Enroll'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CourseDashboard;
