import React, { useState, useEffect } from 'react';
import './App.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import axios from 'axios'

function App() {

    const [applicants, setApplicants] = useState<any[]>([]);

    useEffect(() => {
        // Fetch the applicants data when the component mounts
        axios.get('http://localhost:5000/applicants')
            .then(response => {
                console.log("Response data:", response.data);
                setApplicants(response.data.Users);
            })
            .catch(error => {
                console.error("Error fetching applicants:", error);

            });
    }, []);

    const [selectedApplicant, setSelectedApplicant] = useState<any | null>(null);

    const handleRowClick = (applicant: any) => {
        setSelectedApplicant(applicant);
    };

    const startApplicationProcess = () => {
        if (selectedApplicant) {
            // Start the application process for the selected applicant

            console.log("Starting application process for:", selectedApplicant.UserName);
            // You can make API calls or other actions here
        }
    };

    const [username, setUsername] = useState<string>("");
    const handleUsernameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setUsername(event.target.value);
    };


    const [showModal, setShowModal] = useState<boolean>(false);

    const openModal = () => {
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
    };

    const handleAddUser = () => {
        axios.post('http://localhost:5000/applicants', { user_name: username })
            .then(response => {
                console.log("User added:", response.data);
                // Close the modal after successful addition
                closeModal();
                // Optionally, you can refresh the list of applicants here
            })
            .catch(error => {
                console.error("Error adding user:", error);
            });
    };

    return (
        <div className="container">
            <h1 className="text-center mt-5">Applicant Manager</h1>
            <table className="table mt-4">
                <thead>
                    <tr>
                        <th>Path</th>
                        <th>UserName</th>
                        <th>UserId</th>
                        <th>Arn</th>
                        <th>CreateDate</th>
                        <th>PasswordLastUsed</th>
                        <th>PermissionsBoundaryType</th>
                        <th>PermissionsBoundaryArn</th>
                        <th>Tags</th>
                    </tr>
                </thead>
                <tbody>
                    {applicants.map((applicant, index) => (
                        <tr key={index}
                        onClick={() => handleRowClick(applicant)}
                        className={selectedApplicant === applicant ? 'selected-row' : ''}
                        >
                            <td>{applicant.Path}</td>
                            <td>{applicant.UserName}</td>
                            <td>{applicant.UserId}</td>
                            <td>{applicant.Arn}</td>
                            <td>{applicant.CreateDate}</td>
                            <td>{applicant.PasswordLastUsed}</td>
                            <td>{applicant.PermissionsBoundary?.PermissionsBoundaryType}</td>
                            <td>{applicant.PermissionsBoundary?.PermissionsBoundaryArn}</td>
                            <td>
                                {applicant.Tags ? applicant.Tags.map((tag: any) => (
                                    <span key={tag.Key}>{tag.Key}: {tag.Value} </span>
                                )) : 'N/A'}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <button 
              className="btn btn-primary mt-3"
              onClick={startApplicationProcess}
              disabled={!selectedApplicant}
            >
              Start Application process
            </button>
            <button className="btn btn-primary mt-4" onClick={openModal}>
                Add User
            </button>
            {/* Bootstrap Modal */}
            <div className={`modal ${showModal ? 'show' : ''}`} tabIndex={-1} style={showModal ? { display: 'block' } : {}}>
                <div className="modal-dialog">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h5 className="modal-title">Add User</h5>
                            <button type="button" className="btn-close" onClick={closeModal}></button>
                        </div>
                        <div className="modal-body">
                            <input 
                                type="text" 
                                placeholder="Enter username" 
                                value={username} 
                                onChange={handleUsernameChange}
                                className="form-control"
                            />
                        </div>
                        <div className="modal-footer">
                            <button type="button" className="btn btn-secondary" onClick={closeModal}>
                                Close
                            </button>
                            <button type="button" className="btn btn-primary" onClick={handleAddUser}>
                                Add User
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
        </div>
    );
}

export default App;

