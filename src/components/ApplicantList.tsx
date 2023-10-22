import React from 'react';

interface Applicant {
    id: number;
    givenName: string;
    firstName: string;
    email: string;
}

interface Props {

    applicants: Applicant[];
}

const ApplicantsList: React.FC<Props> = ({ applicants }) => {
    return (
        <div>
            <h2>Applicants</h2>
            <ul>
                {applicants.map(applicant => (
                    <li key={applicant.id}>
                        {applicant.givenName} {applicant.firstName} - {applicant.email}
                    </li>
                ))}

            </ul>
        </div>
    );
}

export default ApplicantsList;
