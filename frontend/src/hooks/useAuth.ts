/** Authentication hooks for PehchaanAI Frontend */

import { useAuth } from '../context/AuthContext';

export function useCurrentUser() {
  const { user, isLoading, isAuthenticated } = useAuth();
  
  return {
    data: user,
    isLoading,
    isError: !isLoading && !isAuthenticated,
    error: !isLoading && !isAuthenticated ? new Error('Not authenticated') : null,
  };
}

export function useLogin() {
  const { login } = useAuth();
  
  return {
    mutateAsync: login,
    isPending: false,
    isError: false,
    error: null,
  };
}

export function useRegister() {
  const { register } = useAuth();
  
  return {
    mutateAsync: register,
    isPending: false,
    isError: false,
    error: null,
  };
}

export function useLogout() {
  const { logout } = useAuth();
  
  return {
    mutate: logout,
    isPending: false,
  };
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
