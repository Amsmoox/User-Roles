import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

function App() {
  const [backendStatus, setBackendStatus] = useState<string>('Checking connection...');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Test connection to Django backend
    const testBackendConnection = async () => {
      try {
        // First check if Django server is responding
        const response = await axios.get('http://localhost:8000/api/v1/accounts/permissions/', {
          timeout: 5000 // 5 second timeout
        });
        
        if (response.status === 200) {
          setBackendStatus('Successfully connected to Django backend!');
        } else {
          setBackendStatus(`Connected, but received status: ${response.status}`);
        }
      } catch (err: unknown) {
        console.error('Backend connection error:', err);
        if (axios.isAxiosError(err)) {
          if (err.code === 'ECONNREFUSED') {
            setError('Cannot connect to Django backend. Is the server running?');
          } else if (err.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            setError(`Backend responded with status: ${err.response.status}`);
          } else if (err.request) {
            // The request was made but no response was received
            setError('Backend not responding. Make sure Django server is running on port 8000.');
          } else {
            // Something happened in setting up the request that triggered an Error
            setError(`Error: ${err.message}`);
          }
        } else {
          setError(`Unexpected error occurred: ${String(err)}`);
        }
      }
    };

    testBackendConnection();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>User Roles System</h1>
        <div className="connection-status">
          <h2>Backend Connection Status:</h2>
          <p className={error ? 'status-error' : 'status-success'}>
            {error ? error : backendStatus}
          </p>
          {error && (
            <div className="error-help">
              <h3>Troubleshooting:</h3>
              <ol>
                <li>Make sure Django server is running on http://localhost:8000</li>
                <li>Check CORS settings in Django</li>
                <li>Verify API endpoints are correctly configured</li>
              </ol>
            </div>
          )}
        </div>
      </header>
    </div>
  );
}

export default App; 