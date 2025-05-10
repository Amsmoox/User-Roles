import Image from "next/image";
import ApiTest from "./components/ApiTest";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <main className="flex flex-col items-center gap-10 w-full max-w-4xl">
        <h1 className="text-4xl font-bold mb-4 text-center">User Roles System</h1>
        
        <div className="w-full p-8 bg-white shadow-lg rounded-lg">
          <h2 className="text-2xl font-semibold text-center mb-6">Backend Connection Test</h2>
          <p className="text-gray-600 mb-6 text-center">
            Click the button below to check if the backend API is accessible.
          </p>
          
          <ApiTest />
        </div>
        
        <div className="text-center mt-8 text-gray-500 text-sm">
          <p>
            This system provides a comprehensive role-based permission system with 
            optimal performance, security features, and comprehensive authentication.
          </p>
        </div>
      </main>
    </div>
  );
}
