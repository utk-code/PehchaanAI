import { useEffect, useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import {
    LayoutDashboard,
    FileSearch,
    Search,
    FileText,
    LogOut,
    Menu,
    X,
    ShieldCheck,
    User,
    Plus,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/cases', label: 'Cases', icon: FileSearch },
    { path: '/search', label: 'Search', icon: Search },
    { path: '/reports', label: 'Reports', icon: FileText },
];

function useIsDesktop() {
    const [isDesktop, setIsDesktop] = useState(() => window.matchMedia('(min-width: 1024px)').matches);

    useEffect(() => {
        const mq = window.matchMedia('(min-width: 1024px)');
        const onChange = (e: MediaQueryListEvent) => setIsDesktop(e.matches);
        mq.addEventListener('change', onChange);
        return () => mq.removeEventListener('change', onChange);
    }, []);

    return isDesktop;
}

export function Layout() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const reducedMotion = useReducedMotion();
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const isDesktop = useIsDesktop();
    const sidebarVisible = isDesktop || sidebarOpen;

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="min-h-screen bg-atmosphere relative">
            <AnimatePresence>
                {sidebarOpen && (
                    <motion.div
                        className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setSidebarOpen(false)}
                    />
                )}
            </AnimatePresence>

            <motion.aside
                className="fixed inset-y-0 left-0 z-50 w-72 border-r border-white/5 bg-ocean-950/90 backdrop-blur-xl lg:bg-ocean-950/60 flex flex-col"
                initial={reducedMotion ? false : { x: -280, opacity: 0 }}
                animate={
                    reducedMotion
                        ? {}
                        : sidebarVisible
                            ? { x: 0, opacity: 1 }
                            : { x: -280, opacity: 0 }
                }
                transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                aria-hidden={!sidebarVisible}
            >
                <div className="flex items-center justify-between px-6 py-6">
                    <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center shadow-glow-brand">
                            <ShieldCheck className="h-5 w-5 text-white" />
                        </div>
                        <div>
                            <h1 className="font-display font-bold text-white tracking-tight text-lg leading-tight">
                                PehchaanAI
                            </h1>
                            <p className="text-[11px] text-white/40 tracking-widest uppercase">
                                Investigation OS
                            </p>
                        </div>
                    </div>
                    <button
                        className="lg:hidden p-2 text-white/60 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                        onClick={() => setSidebarOpen(false)}
                        aria-label="Close navigation menu"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>

                <div className="px-6 pb-4">
                    <button
                        onClick={() => navigate('/cases/new')}
                        className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-brand-500 to-violet-600 text-white font-medium text-sm hover:shadow-glow-brand hover:-translate-y-0.5 transition-all duration-200"
                    >
                        <Plus className="h-4 w-4" />
                        New Case
                    </button>
                </div>

                <nav className="flex-1 px-4 space-y-1">
                    <p className="px-3 pb-2 text-[11px] font-medium tracking-widest uppercase text-white/30">
                        Workspace
                    </p>
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            onClick={() => setSidebarOpen(false)}
                            className={({ isActive }) => `
                                relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-200
                                ${isActive
                                    ? 'bg-white/5 text-white'
                                    : 'text-white/50 hover:text-white hover:bg-white/[0.03]'
                                }
                            `}
                        >
                            {({ isActive }) => (
                                <>
                                    {isActive && (
                                        <motion.span
                                            layoutId="active-nav"
                                            className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 rounded-full bg-gradient-to-b from-brand-400 to-cyan-400"
                                            transition={{ type: 'spring', stiffness: 400, damping: 35 }}
                                        />
                                    )}
                                    <item.icon
                                        className={`h-4.5 w-4.5 ${
                                            isActive ? 'text-brand-400' : 'group-hover:text-white'
                                        }`}
                                        strokeWidth={2}
                                    />
                                    <span>{item.label}</span>
                                </>
                            )}
                        </NavLink>
                    ))}
                </nav>

                <div className="p-4 border-t border-white/5">
                    <div className="flex items-center gap-3 px-2 py-3 rounded-lg hover:bg-white/[0.03] transition-colors">
                        <div className="relative">
                            <div className="h-9 w-9 rounded-full bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center text-white text-sm font-semibold">
                                {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                            </div>
                            <div className="absolute bottom-0 right-0 h-2.5 w-2.5 bg-emerald-400 rounded-full border-2 border-ocean-950" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate">
                                {user?.full_name || 'User'}
                            </p>
                            <p className="text-xs text-white/40 truncate">{user?.email}</p>
                        </div>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="mt-1 w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-white/50 hover:text-rose-400 hover:bg-rose-500/5 transition-colors duration-200"
                    >
                        <LogOut className="h-4 w-4" />
                        Sign out
                    </button>
                </div>
            </motion.aside>

            <div className="lg:pl-72 relative">
                <header className="sticky top-0 z-30 bg-ocean-950/70 backdrop-blur-xl border-b border-white/5">
                    <div className="flex items-center justify-between h-16 px-4 lg:px-8">
                        <div className="flex items-center gap-4">
                            <button
                                className="lg:hidden p-2 text-white/60 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                                onClick={() => setSidebarOpen(true)}
                                aria-label="Open navigation menu"
                            >
                                <Menu className="h-5 w-5" />
                            </button>
                            <div className="hidden sm:flex items-center gap-2 text-sm text-white/60">
                                <ShieldCheck className="h-4 w-4 text-brand-400" />
                                <span className="font-medium text-white/80">Missing Child Identification</span>
                            </div>
                        </div>

                        <div className="flex items-center gap-3">
                            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-white/5 rounded-lg border border-white/10">
                                <User className="h-3.5 w-3.5 text-white/40" />
                                <span className="text-xs text-white/70">{user?.full_name || 'Investigator'}</span>
                            </div>
                        </div>
                    </div>
                </header>

                <main className="px-4 lg:px-8 py-6 lg:py-8 min-h-[calc(100vh-4rem)] max-w-[1400px] mx-auto w-full">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
