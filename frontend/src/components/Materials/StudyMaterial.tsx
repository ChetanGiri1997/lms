import React from 'react';

interface LessonDetailProps {
    title: string;
    description: string;
    duration: number; // duration in minutes
}

const LessonDetail: React.FC<LessonDetailProps> = ({ title, description, duration }) => {
    return (
        <div className="lesson-detail">
            <h1>{title}</h1>
            <p>{description}</p>
            <p>Duration: {duration} minutes</p>
        </div>
    );
};

export default LessonDetail;