import { NextResponse } from 'next/server';

export async function GET() {
  try {
    console.log('Testing connection to Django backend...');
    
    // Try multiple approaches to connect to the Django backend
    const urls = [
      'http://127.0.0.1:8000/api/v1/accounts/auth/login/',
      'http://localhost:8000/api/v1/accounts/auth/login/'
    ];
    
    let success = false;
    let responseStatus = 0;
    let errorDetails = '';
    
    // Try each URL until one succeeds
    for (const url of urls) {
      try {
        console.log(`Attempting to connect to: ${url}`);
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          signal: AbortSignal.timeout(3000),
        });
        
        responseStatus = response.status;
        console.log(`Connection successful with status: ${response.status}`);
        success = true;
        break;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : String(err);
        errorDetails += `Failed to connect to ${url}: ${errorMessage}. `;
        console.error(`Failed to connect to ${url}:`, err);
      }
    }
    
    if (success) {
      // Return success if we get any response
      return NextResponse.json({ 
        status: 'success', 
        message: `API connection successful! Status: ${responseStatus}`,
        djangoStatus: responseStatus
      });
    } else {
      // All connection attempts failed
      return NextResponse.json(
        { 
          status: 'error', 
          message: 'All connection attempts to the Django backend failed.',
          error: errorDetails
        },
        { status: 500 }
      );
    }
  } catch (error) {
    // Return error if connection fails
    console.error('Backend connection test failed:', error);
    return NextResponse.json(
      { 
        status: 'error', 
        message: 'API connection failed! Make sure your Django backend is running on port 8000.',
        error: error instanceof Error ? error.message : String(error)
      },
      { status: 500 }
    );
  }
} 