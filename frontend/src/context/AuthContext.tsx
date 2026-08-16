/** Authentication Context for PehchaanAI Frontend */

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authApi } from '../services/api';

export interface User {
    id: string;
    email: string;
    full_name: string;
    created_at: string;
}

interface AuthContextType {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    login: (credentials: { username: string; password: string }) => Promise<void>;
    register: (data: { email: string; full_name: string; password: string }) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            authApi.me()
                .then((data) => setUser(data))
                .catch(() => {
                    localStorage.removeItem('access_token');
                    setUser(null);
                })
                .finally(() => setIsLoading(false));
        } else {
            setIsLoading(false);
        }
    }, []);

    const login = async (credentials: { username: string; password: string }) => {
        const data = await authApi.login(credentials);
        localStorage.setItem('access_token', data.access_token);
        const userData = await authApi.me();
        setUser(userData);
    };

    const register = async (data: { email: string; full_name: string; password: string }) => {
        const result = await authApi.register(data);
        localStorage.setItem('access_token', result.access_token);
        const userData = await authApi.me();
        setUser(userData);
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        setUser(null);
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                isLoading,
                isAuthenticated: !!user,
                login,
                register,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}