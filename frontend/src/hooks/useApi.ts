import { useMutation, useQuery, QueryKey, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { apiEndpoints, apiRequest } from '../utils/api';
import { AxiosError, AxiosRequestConfig } from 'axios';

// Type for the API endpoint path
type ApiEndpoint = string | ((...args: any[]) => string);

// Helper to resolve endpoint string or function
const resolveEndpoint = (endpoint: ApiEndpoint, ...args: any[]): string => {
  if (typeof endpoint === 'function') {
    return endpoint(...args);
  }
  return endpoint;
};

// Hook for GET requests
export const useApiQuery = <TData = unknown, TError = AxiosError>(
  endpointKey: keyof typeof apiEndpoints | [keyof typeof apiEndpoints, string],
  endpointPath: ApiEndpoint,
  params?: any[],
  options?: Omit<AxiosRequestConfig, 'method' | 'url'> & UseQueryOptions<TData, TError>
) => {
  // Determine the category and specific endpoint
  let category: keyof typeof apiEndpoints;
  let path: ApiEndpoint;
  
  if (Array.isArray(endpointKey)) {
    [category, path] = endpointKey as [keyof typeof apiEndpoints, string];
    endpointPath = apiEndpoints[category][path as keyof typeof apiEndpoints[keyof typeof apiEndpoints]];
  } else {
    category = endpointKey as keyof typeof apiEndpoints;
    path = endpointPath;
  }
  
  // Resolve the endpoint if it's a function
  const resolvedEndpoint = resolveEndpoint(endpointPath, ...(params || []));
  
  // The query key includes the category, path, and any params for proper caching
  const queryKey: QueryKey = [category, path, ...(params || [])];
  
  return useQuery<TData, TError>({
    queryKey,
    queryFn: async () => {
      const response = await apiRequest<TData>('GET', resolvedEndpoint, undefined, options);
      return response.data;
    },
    ...options,
  });
};

// Hook for mutation requests (POST, PUT, PATCH, DELETE)
export const useApiMutation = <TData = unknown, TVariables = unknown, TError = AxiosError>(
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE',
  endpointKey: keyof typeof apiEndpoints | [keyof typeof apiEndpoints, string],
  endpointPath: ApiEndpoint,
  options?: Omit<AxiosRequestConfig, 'method' | 'url' | 'data'> & UseMutationOptions<TData, TError, TVariables>
) => {
  // Determine the category and specific endpoint
  let category: keyof typeof apiEndpoints;
  let path: ApiEndpoint;
  
  if (Array.isArray(endpointKey)) {
    [category, path] = endpointKey as [keyof typeof apiEndpoints, string];
    endpointPath = apiEndpoints[category][path as keyof typeof apiEndpoints[keyof typeof apiEndpoints]];
  } else {
    category = endpointKey as keyof typeof apiEndpoints;
    path = endpointPath;
  }
  
  return useMutation<TData, TError, TVariables>({
    mutationFn: async (variables: TVariables) => {
      // For endpoints with parameters like ID, allow passing them as part of the variables
      let params: any[] = [];
      if (variables && typeof variables === 'object' && 'params' in variables) {
        params = (variables as any).params || [];
        delete (variables as any).params;
      }
      
      // Resolve the endpoint
      const resolvedEndpoint = resolveEndpoint(endpointPath, ...params);
      
      const response = await apiRequest<TData>(method, resolvedEndpoint, variables, options);
      return response.data;
    },
    ...options,
  });
};

// Convenience hooks for different HTTP methods
export const useGetApi = <TData = unknown, TError = AxiosError>(
  endpointKey: keyof typeof apiEndpoints | [keyof typeof apiEndpoints, string],
  endpointPath: ApiEndpoint,
  params?: any[],
  options?: Omit<AxiosRequestConfig, 'method' | 'url'> & UseQueryOptions<TData, TError>
) => useApiQuery<TData, TError>(endpointKey, endpointPath, params, options);

export const usePostApi = <TData = unknown, TVariables = unknown, TError = AxiosError>(
  endpointKey: keyof typeof apiEndpoints | [keyof typeof apiEndpoints, string],
  endpointPath: ApiEndpoint,
  options?: Omit<AxiosRequestConfig, 'method' | 'url' | 'data'> & UseMutationOptions<TData, TError, TVariables>
) => useApiMutation<TData, TVariables, TError>('POST', endpointKey, endpointPath, options);

export const usePutApi = <TData = unknown, TVariables = unknown, TError = AxiosError>(
  endpointKey: keyof typeof apiEndpoints | [keyof typeof apiEndpoints, string],
  endpointPath: ApiEndpoint,
  options?: Omit<AxiosRequestConfig, 'method' | 'url' | 'data'> & UseMutationOptions<TData, TError, TVariables>
) => useApiMutation<TData, TVariables, TError>('PUT', endpointKey, endpointPath, options);

export const usePatchApi = <TData = unknown, TVariables = unknown, TError = AxiosError>(
  endpointKey: keyof typeof apiEndpoints | [keyof typeof apiEndpoints, string],
  endpointPath: ApiEndpoint,
  options?: Omit<AxiosRequestConfig, 'method' | 'url' | 'data'> & UseMutationOptions<TData, TError, TVariables>
) => useApiMutation<TData, TVariables, TError>('PATCH', endpointKey, endpointPath, options);

export const useDeleteApi = <TData = unknown, TVariables = unknown, TError = AxiosError>(
  endpointKey: keyof typeof apiEndpoints | [keyof typeof apiEndpoints, string],
  endpointPath: ApiEndpoint,
  options?: Omit<AxiosRequestConfig, 'method' | 'url' | 'data'> & UseMutationOptions<TData, TError, TVariables>
) => useApiMutation<TData, TVariables, TError>('DELETE', endpointKey, endpointPath, options); 