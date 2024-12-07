import React from 'react';

interface Assignment {
    id: number;
    title: string;
    dueDate: string;
}

interface AssignmentListProps {
    assignments: Assignment[];
}

const AssignmentList: React.FC<AssignmentListProps> = ({ assignments }) => {
    return (
        <div>
            <h2>Assignments</h2>
            <ul>
                {assignments.map((assignment) => (
                    <li key={assignment.id}>
                        <h3>{assignment.title}</h3>
                        <p>Due Date: {assignment.dueDate}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default AssignmentList;