import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate for navigation
import api from '../../utils/api'; // Assuming you have an API setup to handle requests

interface Course {
  id?: string;
  name: string;
  description: string;
  teachers?: string[];
}

interface CourseFormProps {
  courseId?: string; // Optional for editing
  onClose: () => void; // Function to close the form
}

const CourseForm: React.FC<CourseFormProps> = ({ courseId, onClose }) => {
  const [course, setCourse] = useState<Course>({
    name: '',
    description: '',
    teachers: []
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate(); // Initialize useNavigate

  useEffect(() => {
    if (courseId) {
      const fetchCourse = async () => {
        try {
          const response = await api.get(`/api/courses/${courseId}`);
          setCourse(response.data);
        } catch (err) {
          setError((err as Error).message);
        }
      };
      fetchCourse();
    }
  }, [courseId]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setCourse((prev) => ({
      ...prev,
      [name]: name === 'teachers' ? value.split(',').map(teacher => teacher.trim()) : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (courseId) {
        // Edit existing course
        await api.put(`/courses/${courseId}`, course);
      } else {
        // Add new course
        await api.post('/courses', course);
      }
      onClose(); // Close the form on success
      navigate('/dashboard/courses/list'); // Navigate to the course list
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-4 bg-white shadow-lg rounded-lg">
      <h2 className="text-2xl font-semibold text-center mb-4">{courseId ? 'Edit Course' : 'Add Course'}</h2>
      {error && <p className="text-red-500 text-center">{error}</p>}
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block mb-2" htmlFor="name">
            Course Name:
          </label>
          <input
            type="text"
            name="name"
            id="name"
            value={course.name}
            onChange={handleChange}
            required
            className="w-full p-2 border border-gray-300 rounded"
          />
        </div>
        <div className="mb-4">
          <label className="block mb-2" htmlFor="description">
            Description:
          </label>
          <textarea
            name="description"
            id="description"
            value={course.description}
            onChange={handleChange}
            required
            className="w-full p-2 border border-gray-300 rounded"
            rows={4}
          />
        </div>
        <div className="mb-4">
          <label className="block mb-2" htmlFor="teachers">
            Teachers (comma-separated):
          </label>
          <input
            type="text"
            name="teachers"
            id="teachers"
            value={course.teachers?.join(', ')}
            onChange={handleChange}
            className="w-full p-2 border border-gray-300 rounded"
          />
        </div>
        <div className="flex justify-between">
          <button
            type="submit"
            disabled={loading}
            className={`w-full p-2 text-white rounded ${loading ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600'}`}
          >
            {loading ? 'Saving...' : 'Save Course'}
          </button>
          <button
            type="button"
            onClick={onClose}
            className="ml-2 w-full p-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default CourseForm;
