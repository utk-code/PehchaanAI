/** Protected Route Component - requires authentication */

import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

interface ProtectedRouteProps {
    children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
    const { isAuthenticated, isLoading } = useAuth();
    const location = useLocation();

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-atmosphere">
                <div className="flex flex-col items-center gap-4">
                    <div className="relative">
                        <span className="absolute inset-0 rounded-lg bg-brand-500/40 animate-pulse-ring" />
                        <div className="relative h-10 w-10 rounded-lg bg-gradient-to-br from-brand-500 to-violet-600 shadow-glow-brand"></div>
                    </div>
                    <p className="font-mono text-[10px] tracking-[0.28em] uppercase text-white/45">
                        Verifying session<span className="terminal-caret" aria-hidden />
                    </p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return <>{children}</>;
}