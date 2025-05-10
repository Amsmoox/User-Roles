// API service for making requests to the backend

// Type for API test response
interface ApiTestResponse {
  status: 'success' | 'error';
  message: string;
  djangoStatus?: number;
  error?: string;
}

/**
 * Tests the connection to the Django backend
 * @returns Promise with the API connection status
 */
export const testApiConnection = async (): Promise<ApiTestResponse> => {
  try {
    // Use our Next.js API route to test the connection
    const response = await fetch('/api/test-connection', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Set a timeout of 8 seconds
      signal: AbortSignal.timeout(8000),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      return { 
        status: 'error', 
        message: errorData.message || 'API connection failed!',
        error: errorData.error
      };
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API connection test failed:', error);
    return { 
      status: 'error', 
      message: 'API connection failed! Network error or timeout.',
      error: error instanceof Error ? error.message : String(error)
    };
  }
}; 