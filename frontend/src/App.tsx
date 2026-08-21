/** Main App Component with Routing */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/layout/Layout';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { CaseListPage } from './pages/CaseListPage';
import { CaseCreatePage } from './pages/CaseCreatePage';
import { CaseDetailPage } from './pages/CaseDetailPage';
import { SearchPage } from './pages/SearchPage';
import { ReportsPage } from './pages/ReportsPage';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import './styles.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function AppRoutes() {
  const { isLoading, isAuthenticated } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-atmosphere relative overflow-hidden">
        <div className="absolute top-24 -left-24 w-96 h-96 rounded-full border border-brand-500/15 animate-float" />
        <div className="absolute -bottom-32 right-0 w-[520px] h-[520px] rounded-full border border-cyan-400/10 animate-float-slow" />
        <div className="flex flex-col items-center gap-4">
          <div className="relative">
            <span className="absolute inset-0 rounded-lg bg-brand-500/40 animate-pulse-ring" />
            <div className="relative h-10 w-10 rounded-lg bg-gradient-to-br from-brand-500 to-violet-600 shadow-glow-brand"></div>
          </div>
          <p className="font-mono text-[10px] tracking-[0.28em] uppercase text-white/45">
            Initializing PehchaanAI<span className="terminal-caret" aria-hidden />
          </p>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />
        }
      />
      <Route
        path="/register"
        element={
          isAuthenticated ? <Navigate to="/dashboard" replace /> : <RegisterPage />
        }
      />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="cases" element={<CaseListPage />} />
        <Route path="cases/new" element={<CaseCreatePage />} />
        <Route path="cases/:caseId" element={<CaseDetailPage />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="reports" element={<ReportsPage />} />
      </Route>
    </Routes>
  );
}

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
