import React from 'react';

interface Lesson {
    id: number;
    title: string;
    description: string;
}

interface LessonListProps {
    lessons: Lesson[];
}

const LessonList: React.FC<LessonListProps> = ({ lessons }) => {
    return (
        <div>
            <h2>Lesson List</h2>
            <ul>
                {lessons.map((lesson) => (
                    <li key={lesson.id}>
                        <h3>{lesson.title}</h3>
                        <p>{lesson.description}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default LessonList;