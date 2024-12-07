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
  students?: { _id: string }[]; // Optional students list
}

const CourseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isActionLoading, setIsActionLoading] = useState<boolean>(false);

  // Fetch course details
  const fetchCourseDetails = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/courses/${id}`);
      setCourse(response.data.course);
    } catch (err) {
      setError((err as Error).message || 'Failed to fetch course details');
    } finally {
      setLoading(false);
    }
  };

  // Handle course enrollment/opt-out
  const handleCourseAction = async () => {
    if (!course) return;

    try {
      setIsActionLoading(true);
      if (course.enrolled) {
        await api.post(`/courses/${id}/optout`);
      } else {
        await api.post(`/courses/${id}/enroll`);
      }
      await fetchCourseDetails(); // Refresh course details
    } catch (err) {
      setError((err as Error).message || 'Action failed');
    } finally {
      setIsActionLoading(false);
    }
  };

  // Effect to fetch course data when the component mounts
  useEffect(() => {
    fetchCourseDetails();
  }, [id]);

  if (loading) return <div>Loading course details...</div>;
  if (error) return <div className="text-red-500">Error: {error}</div>;
  if (!course) return <div>No course found.</div>;

  return (
    <div className="container mx-auto p-6 max-w-2xl">
      <h1 className="text-3xl font-bold mb-6">{course.name}</h1>
      
      <div className="bg-white p-6 rounded-lg shadow-md space-y-4">
        {/* Course Description */}
        <div>
          <h2 className="text-xl font-semibold mb-2">Description</h2>
          <p className="text-gray-600">{course.description}</p>
        </div>

        {/* Instructors */}
        <div>
          <h2 className="text-lg font-semibold mb-2">Instructor(s):</h2>
          {course.teachers && course.teachers.length > 0 ? (
            <ul className="space-y-1">
              {course.teachers.map((teacher) => (
                <li key={teacher.id} className="text-gray-700">
                  {teacher.name} {teacher.email && `(${teacher.email})`}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">No instructors assigned.</p>
          )}
        </div>

        {/* Course Owner */}
        <div>
          <h2 className="text-lg font-semibold mb-2">Course Owner:</h2>
          <p className="text-gray-700">
            {course.owner.name} - {course.owner.role}
          </p>
        </div>

        {/* Course Status */}
        <div>
          <h2 className="text-lg font-semibold mb-2">Course Status:</h2>
          <p className={`font-medium ${course.archived ? 'text-red-600' : 'text-green-600'}`}>
            {course.archived ? 'Archived' : 'Active'}
          </p>
        </div>

        {/* Student Count (Optional) */}
        {course.students && (
          <div>
            <h2 className="text-lg font-semibold mb-2">Enrolled Students:</h2>
            <p>{course.students.length}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-4 pt-4 border-t">
          <Link
            to="/courses"
            className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
          >
            Back to Courses
          </Link>
          
          {!course.archived && (
            <button
              className={`px-4 py-2 rounded-md transition-colors ${
                course.enrolled
                  ? 'bg-yellow-500 hover:bg-yellow-600'
                  : 'bg-green-500 hover:bg-green-600'
              } text-white ${isActionLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={handleCourseAction}
              disabled={isActionLoading}
            >
              {isActionLoading 
                ? 'Processing...' 
                : (course.enrolled ? 'Opt-Out' : 'Enroll')
              }
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CourseDetail;