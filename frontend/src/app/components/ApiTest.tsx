'use client';

import { useState } from 'react';
import { testApiConnection } from '../api/api';

// API status type
interface ApiStatus {
  status: 'success' | 'error';
  message: string;
  djangoStatus?: number;
  error?: string;
}

/**
 * Component that displays a button to test the API connection
 */
export default function ApiTest() {
  // State for API status and loading state
  const [apiStatus, setApiStatus] = useState<ApiStatus | null>(null);
  const [loading, setLoading] = useState(false);

  // Handle API test button click
  const handleTestApiConnection = async () => {
    setLoading(true);
    try {
      const result = await testApiConnection();
      setApiStatus(result);
    } catch (error) {
      console.error('Error testing API connection:', error);
      setApiStatus({ 
        status: 'error', 
        message: 'An unexpected error occurred',
        error: error instanceof Error ? error.message : String(error)
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <button 
        onClick={handleTestApiConnection} 
        disabled={loading}
        className={`
          px-4 py-3 rounded-md font-medium text-white 
          ${loading ? 'bg-gray-400' : 'bg-green-600 hover:bg-green-700'}
          transition-colors duration-200 disabled:cursor-not-allowed
        `}
      >
        {loading ? 'Testing...' : 'Test API Connection'}
      </button>
      
      {apiStatus && (
        <div className={`
          p-4 rounded-md w-full max-w-md mt-4 text-center
          ${apiStatus.status === 'success' ? 'bg-green-100 text-green-800 border border-green-200' : 
            'bg-red-100 text-red-800 border border-red-200'}
        `}>
          <p className="font-medium mb-2">{apiStatus.message}</p>
          
          {apiStatus.djangoStatus && (
            <p className="text-sm mt-1">Django Status Code: {apiStatus.djangoStatus}</p>
          )}
          
          {apiStatus.error && (
            <p className="text-sm mt-3 p-2 bg-red-50 border border-red-200 rounded">
              Error Details: {apiStatus.error}
            </p>
          )}
        </div>
      )}
    </div>
  );
} 