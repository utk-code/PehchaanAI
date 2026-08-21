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
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, code: '01' },
    { path: '/cases', label: 'Cases', icon: FileSearch, code: '02' },
    { path: '/search', label: 'Search', icon: Search, code: '03' },
    { path: '/reports', label: 'Reports', icon: FileText, code: '04' },
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
            <div className="grain" aria-hidden />

            <AnimatePresence>
                {sidebarOpen && (
                    <motion.div
                        className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setSidebarOpen(false)}
                    />
                )}
            </AnimatePresence>

            <motion.aside
                className="fixed inset-y-0 left-0 z-50 w-72 border-r border-white/10 bg-ocean-950/95 backdrop-blur-xl lg:bg-ocean-950/70 flex flex-col"
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
                <div className="px-5 pt-6 pb-2">
                    <div className="relative rounded-xl bg-white/[0.03] border border-white/10 p-4 tick-corners">
                        <div className="flex items-center gap-3">
                            <div className="relative flex items-center justify-center">
                                <span className="absolute inset-0 rounded-lg bg-brand-500/40 animate-pulse-ring" />
                                <div className="relative h-10 w-10 rounded-lg bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center shadow-glow-brand">
                                    <ShieldCheck className="h-5 w-5 text-white" />
                                </div>
                            </div>
                            <div className="min-w-0">
                                <h1 className="font-display font-bold text-white tracking-tight text-lg leading-tight truncate">
                                    Pehchaan<span className="text-gradient">AI</span>
                                </h1>
                                <p className="font-mono text-[10px] text-white/40 tracking-[0.22em] uppercase mt-0.5">
                                    Face Forensics OS
                                </p>
                            </div>
                        </div>
                        <div className="mt-3 pt-3 border-t border-white/10 flex items-center gap-2 font-mono text-[10px] tracking-wide text-white/35">
                            <span className="beacon-dot" />
                            SIGNAL&nbsp;/&nbsp;LIVE
                            <span className="ml-auto text-brand-400/70">v0.1.0</span>
                        </div>
                    </div>
                    <button
                        className="lg:hidden absolute top-5 right-4 p-2 text-white/60 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                        onClick={() => setSidebarOpen(false)}
                        aria-label="Close navigation menu"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>

                <div className="px-5 pb-3">
                    <button
                        onClick={() => navigate('/cases/new')}
                        className="group relative w-full flex items-center justify-center gap-2 py-3 rounded-lg bg-gradient-to-r from-brand-500 to-violet-600 text-white font-medium text-sm hover:shadow-glow-brand hover:-translate-y-0.5 transition-all duration-200 overflow-hidden"
                    >
                        <span aria-hidden className="pointer-events-none absolute inset-y-0 -left-1/3 w-1/3 bg-gradient-to-r from-transparent via-white/40 to-transparent skew-x-[-20deg] group-hover:animate-[btn-flash_0.7s_ease]" />
                        <Plus className="h-4 w-4" />
                        New Case
                    </button>
                </div>

                <nav className="flex-1 px-4 space-y-1 pt-2">
                    <p className="px-2 pb-2 mono-label">Workspace / Registry</p>
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            onClick={() => setSidebarOpen(false)}
                            className={({ isActive }) => `
                                relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-200
                                ${isActive
                                    ? 'bg-white/[0.06] text-white'
                                    : 'text-white/50 hover:text-white hover:bg-white/[0.03]'
                                }
                            `}
                        >
                            {({ isActive }) => (
                                <>
                                    {isActive && (
                                        <motion.span
                                            layoutId="active-nav"
                                            className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-6 rounded-full bg-gradient-to-b from-brand-400 to-brand-600 shadow-glow-brand"
                                            transition={{ type: 'spring', stiffness: 400, damping: 35 }}
                                        />
                                    )}
                                    <span className={`font-mono text-[10px] w-4 ${isActive ? 'text-brand-400' : 'text-white/25'}`}>
                                        {item.code}
                                    </span>
                                    <item.icon
                                        className={`h-4.5 w-4.5 ${isActive ? 'text-brand-400' : ''}`}
                                        strokeWidth={2}
                                    />
                                    <span>{item.label}</span>
                                </>
                            )}
                        </NavLink>
                    ))}
                </nav>

                <div className="p-4 border-t border-white/10">
                    <div className="px-2 pb-2 mono-label">Operative</div>
                    <div className="flex items-center gap-3 px-2 py-3 rounded-lg hover:bg-white/[0.03] transition-colors">
                        <div className="relative">
                            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center text-white text-sm font-semibold font-display">
                                {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                            </div>
                            <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 bg-emerald-400 rounded-full border-2 border-ocean-950 animate-pulse" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate">
                                {user?.full_name || 'User'}
                            </p>
                            <p className="font-mono text-[10px] text-white/40 truncate">{user?.email}</p>
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

                <div className="font-mono text-[9px] tracking-[0.18em] uppercase text-white/25 px-5 pb-4">
                    PehchaanAI · Investigation Terminal
                </div>
            </motion.aside>

            <div className="lg:pl-72 relative">
                <header className="sticky top-0 z-30 bg-ocean-950/80 backdrop-blur-xl border-b border-white/10">
                    <div className="relative">
                        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-brand-500/0 via-brand-500/70 to-cyan-400/0" />
                        <div className="flex items-center justify-between h-14 px-4 lg:px-8">
                            <div className="flex items-center gap-4">
                                <button
                                    className="lg:hidden p-2 -ml-2 text-white/60 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                                    onClick={() => setSidebarOpen(true)}
                                    aria-label="Open navigation menu"
                                >
                                    <Menu className="h-5 w-5" />
                                </button>
                                <div className="hidden sm:flex items-center gap-2.5">
                                    <ShieldCheck className="h-4 w-4 text-brand-400" />
                                    <span className="font-mono text-[11px] tracking-[0.18em] uppercase text-white/55">
                                        Missing Child Identification
                                    </span>
                                </div>
                            </div>

                            <div className="flex items-center gap-3">
                                <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-white/[0.04] rounded-md border border-white/10">
                                    <User className="h-3.5 w-3.5 text-brand-400/70" />
                                    <span className="font-mono text-[11px] text-white/70">{user?.full_name || 'Investigator'}</span>
                                </div>
                            </div>
                        </div>
                        <div className="scanline" aria-hidden />
                    </div>
                </header>

                <main className="px-4 lg:px-8 py-6 lg:py-8 min-h-[calc(100vh-3.5rem)] max-w-[1400px] mx-auto w-full relative">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}