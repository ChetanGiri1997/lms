import React from 'react';

interface AssignmentDetailProps {
    title: string;
    description: string;
    dueDate: string;
}

const AssignmentDetail: React.FC<AssignmentDetailProps> = ({ title, description, dueDate }) => {
    return (
        <div className="assignment-detail">
            <h1>{title}</h1>
            <p>{description}</p>
            <p>Due Date: {dueDate}</p>
        </div>
    );
};

export default AssignmentDetail;