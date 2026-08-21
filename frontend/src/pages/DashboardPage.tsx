import { Link } from 'react-router-dom';
import { motion, useReducedMotion } from 'framer-motion';
import {
    FileSearch,
    UploadCloud,
    TrendingUp,
    Clock,
    ArrowRight,
    AlertCircle,
    Users,
    Activity,
    Search,
    Plus,
} from 'lucide-react';
import { useCases } from '../hooks/useCases';
import { useCurrentUser } from '../hooks/useAuth';
import { Reveal, Stagger, StaggerItem, EASE } from '../components/motion/primitives';

const statConfig = {
    active: {
        icon: Activity,
        label: 'Active cases',
        className: 'text-emerald-400',
        bg: 'bg-emerald-400/10',
        ring: 'ring-emerald-400/20',
    },
    total: {
        icon: FileSearch,
        label: 'Total cases',
        className: 'text-brand-400',
        bg: 'bg-brand-400/10',
        ring: 'ring-brand-400/20',
    },
    recent: {
        icon: Clock,
        label: 'Recent (30d)',
        className: 'text-cyan-400',
        bg: 'bg-cyan-400/10',
        ring: 'ring-cyan-400/20',
    },
    searches: {
        icon: Search,
        label: 'Quick actions',
        className: 'text-violet-400',
        bg: 'bg-violet-400/10',
        ring: 'ring-violet-400/20',
    },
};

export function DashboardPage() {
    const { data: user } = useCurrentUser();
    const { data: cases, isLoading, error } = useCases({ limit: 50 });
    const reducedMotion = useReducedMotion();

    const activeCases = cases?.filter((c) => c.status === 'active').length || 0;
    const totalCases = cases?.length || 0;
    const recentCases = cases?.filter((c) => {
        const d = new Date(c.created_at);
        const thirtyDays = 30 * 24 * 60 * 60 * 1000;
        return Date.now() - d.getTime() < thirtyDays;
    }).length || 0;

    const stats = [
        { ...statConfig.active, value: activeCases },
        { ...statConfig.total, value: totalCases },
        { ...statConfig.recent, value: recentCases },
        { ...statConfig.searches, value: 4 },
    ];

    const quickActions = [
        { to: '/cases/new', icon: UploadCloud, label: 'New Case', desc: 'Upload a photo', gradient: 'from-brand-500 to-violet-600' },
        { to: '/cases', icon: FileSearch, label: 'View Cases', desc: `${activeCases} active`, gradient: 'from-emerald-500 to-cyan-500' },
        { to: '/search', icon: Search, label: 'Quick Search', desc: 'Search database', gradient: 'from-amber-500 to-orange-500' },
    ];

    const firstName = user?.full_name?.split(' ')[0] || 'Investigator';

    return (
        <div className="space-y-8 relative">
            {/* Hero */}
            <div className="relative">
                <div className="absolute -top-10 right-0 w-72 h-72 rounded-full border border-brand-500/15 blur-[30px] pointer-events-none" />
                <div className="absolute bottom-0 left-1/3 w-64 h-64 rounded-full border border-cyan-400/10 blur-[24px] pointer-events-none" />

                <motion.div
                    initial={reducedMotion ? false : { opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.7, ease: EASE }}
                >
                    <div className="flex items-center gap-3 mb-3">
                        <span className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-emerald-400/10 text-emerald-300 text-xs font-medium font-mono uppercase tracking-widest">
                            <span className="relative flex h-2 w-2">
                                <span className="absolute inset-0 rounded-full bg-emerald-400 animate-ping" />
                                <span className="relative rounded-full bg-emerald-400 w-2 h-2" />
                            </span>
                            Welcome back
                        </span>
                        <span className="font-mono text-[10px] tracking-[0.25em] uppercase text-white/30">
                            /OPERATIVE {firstName.toUpperCase()}
                        </span>
                    </div>
                    <h1 className="text-4xl lg:text-6xl font-display font-bold text-white tracking-tight leading-none">
                        {firstName}
                    </h1>
                    <p className="mt-3 text-white/50 max-w-xl text-sm lg:text-base">
                        Your investigation workspace is ready. Track cases, search the database, and identify matches.
                    </p>
                </motion.div>
            </div>

            {/* Stats */}
            <Stagger className="grid grid-cols-2 lg:grid-cols-4 gap-4" staggerDelay={0.06}>
                {stats.map((stat) => (
                    <StaggerItem key={stat.label}>
                        <div className="group card-glass rounded-xl p-5 tick-corners hover:bg-white/[0.05] hover:-translate-y-0.5 transition-all duration-200">
                            <div className="flex items-start justify-between">
                                <div>
                                    <p className="font-mono text-[10px] uppercase tracking-widest text-white/40">{stat.label}</p>
                                    <p className="mt-2 text-4xl font-display font-bold text-white">
                                        {isLoading ? (
                                            <span className="inline-block h-8 w-12 bg-white/10 rounded-md animate-pulse" />
                                        ) : (
                                            stat.value
                                        )}
                                    </p>
                                </div>
                                <div className={`p-2.5 rounded-lg ${stat.bg} ring-1 ${stat.ring}`}>
                                    <stat.icon className={`h-5 w-5 ${stat.className}`} />
                                </div>
                            </div>
                        </div>
                    </StaggerItem>
                ))}
            </Stagger>

            {/* Quick actions */}
            <div>
                <div className="flex items-center justify-between mb-4">
                    <h2 className="mono-label">Quick Actions</h2>
                </div>
                <Stagger className="grid grid-cols-1 sm:grid-cols-3 gap-4" staggerDelay={0.05}>
                    {quickActions.map((action) => (
                        <StaggerItem key={action.to}>
                            <Link
                                to={action.to}
                                className="group flex items-center gap-4 card-glass rounded-xl p-5 tick-corners hover:bg-white/[0.05] hover:-translate-y-0.5 transition-all duration-200"
                            >
                                <div className={`p-3 rounded-lg bg-gradient-to-br ${action.gradient} group-hover:scale-105 transition-transform duration-200`}>
                                    <action.icon className="h-5 w-5 text-white" />
                                </div>
                                <div className="flex-1">
                                    <h3 className="font-medium text-white group-hover:text-brand-300 transition-colors">
                                        {action.label}
                                    </h3>
                                    <p className="text-sm text-white/40 mt-0.5">{action.desc}</p>
                                </div>
                                <ArrowRight className="h-4 w-4 text-white/20 group-hover:text-brand-300 group-hover:translate-x-0.5 transition-all" />
                            </Link>
                        </StaggerItem>
                    ))}
                </Stagger>
            </div>

            {/* Main content */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Cases overview */}
                <Reveal delay={0.1} className="lg:col-span-1">
                    <div className="card-glass rounded-xl p-6 h-full tick-corners">
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center gap-2">
                                <Activity className="h-4 w-4 text-brand-400" />
                                <h2 className="font-display font-semibold text-white">Overview</h2>
                            </div>
                            <span className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-widest text-white/40">
                                <span className="beacon-dot" />
                                Live
                            </span>
                        </div>

                        {error ? (
                            <div className="flex items-center gap-3 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl">
                                <AlertCircle className="h-5 w-5 text-rose-400 flex-shrink-0" />
                                <p className="text-sm text-rose-300">Failed to load cases</p>
                            </div>
                        ) : (
                            <>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-4xl font-display font-bold text-white">
                                            {isLoading ? '—' : activeCases}
                                        </p>
                                        <p className="text-sm text-white/40 mt-1">Active cases</p>
                                    </div>
                                    <div className="relative h-20 w-20">
                                        <svg className="h-full w-full -rotate-90" viewBox="0 0 80 80">
                                            <circle
                                                cx="40" cy="40" r="34"
                                                className="stroke-white/10" strokeWidth="6" fill="none"
                                            />
                                            <motion.circle
                                                cx="40" cy="40" r="34"
                                                className="stroke-brand-400"
                                                strokeWidth="6"
                                                fill="none"
                                                strokeLinecap="round"
                                                strokeDasharray={2 * Math.PI * 34}
                                                initial={reducedMotion ? false : { strokeDashoffset: 2 * Math.PI * 34 }}
                                                animate={{
                                                    strokeDashoffset: 2 * Math.PI * 34 * (1 - (totalCases > 0 ? activeCases / totalCases : 0)),
                                                }}
                                                transition={{ duration: 1.2, ease: EASE, delay: 0.3 }}
                                            />
                                        </svg>
                                        <div className="absolute inset-0 flex items-center justify-center">
                                            <span className="text-sm font-semibold text-white">
                                                {totalCases > 0 ? Math.round((activeCases / totalCases) * 100) : 0}%
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <div className="mt-6 space-y-3">
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="flex items-center gap-2 text-white/50">
                                            <span className="h-2 w-2 rounded-full bg-emerald-400" />
                                            Active
                                        </span>
                                        <span className="font-medium text-white">{activeCases}</span>
                                    </div>
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="flex items-center gap-2 text-white/50">
                                            <span className="h-2 w-2 rounded-full bg-white/20" />
                                            Archived
                                        </span>
                                        <span className="font-medium text-white">{totalCases - activeCases}</span>
                                    </div>
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="flex items-center gap-2 text-white/50">
                                            <span className="h-2 w-2 rounded-full bg-cyan-400" />
                                            Total
                                        </span>
                                        <span className="font-medium text-white">{totalCases}</span>
                                    </div>
                                </div>
                            </>
                        )}
                    </div>
                </Reveal>

                {/* Recent cases */}
                <Reveal delay={0.15} className="lg:col-span-2">
                    <div className="card-glass rounded-xl p-6 h-full tick-corners-cyan tick-corners">
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center gap-2">
                                <Clock className="h-4 w-4 text-violet-400" />
                                <h2 className="font-display font-semibold text-white">Recent Cases</h2>
                            </div>
                            <Link
                                to="/cases"
                                className="flex items-center gap-1 text-sm text-brand-400 hover:text-brand-300 transition-colors"
                            >
                                View all
                                <ArrowRight className="h-3.5 w-3.5" />
                            </Link>
                        </div>

                        {isLoading ? (
                            <div className="space-y-3">
                                {[1, 2, 3, 4].map((i) => (
                                    <div key={i} className="h-14 bg-white/5 rounded-xl animate-pulse" />
                                ))}
                            </div>
                        ) : error ? (
                            <div className="flex items-center gap-3 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl">
                                <AlertCircle className="h-5 w-5 text-rose-400 flex-shrink-0" />
                                <p className="text-sm text-rose-300">Failed to load cases</p>
                            </div>
                        ) : cases && cases.length > 0 ? (
                            <div className="space-y-2">
                                {cases.slice(0, 5).map((caseItem, index) => (
                                    <motion.div
                                        key={caseItem.id}
                                        initial={reducedMotion ? false : { opacity: 0, y: 12 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ duration: 0.4, ease: EASE, delay: 0.1 + index * 0.06 }}
                                    >
                                        <Link
                                            to={`/cases/${caseItem.id}`}
                                            className="group flex items-center justify-between p-3.5 rounded-xl hover:bg-white/[0.04] transition-colors duration-200"
                                        >
                                            <div className="flex items-center gap-3 min-w-0 flex-1">
                                                <div className="h-9 w-9 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0">
                                                    <Users className="h-4 w-4 text-white/40" />
                                                </div>
                                                <div className="min-w-0">
                                                    <p className="font-medium text-white truncate group-hover:text-brand-300 transition-colors">
                                                        {caseItem.query_name || 'Unnamed Case'}
                                                    </p>
                                                    <p className="text-xs text-white/40 mt-0.5 flex items-center gap-1.5">
                                                        <Clock className="h-3 w-3" />
                                                        {new Date(caseItem.created_at).toLocaleDateString()}
                                                    </p>
                                                </div>
                                            </div>
                                            <span
                                                className={`px-2.5 py-1 text-xs font-medium rounded-full flex-shrink-0 ${
                                                    caseItem.status === 'active'
                                                        ? 'bg-emerald-400/10 text-emerald-300'
                                                        : 'bg-white/5 text-white/50'
                                                }`}
                                            >
                                                {caseItem.status}
                                            </span>
                                        </Link>
                                    </motion.div>
                                ))}
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-12 text-center">
                                <div className="h-14 w-14 rounded-xl bg-white/5 flex items-center justify-center mb-4">
                                    <FileSearch className="h-6 w-6 text-white/30" />
                                </div>
                                <p className="text-white/60 font-medium">No cases yet</p>
                                <p className="text-sm text-white/40 mt-1 mb-5">Create your first case to get started</p>
                                <Link
                                    to="/cases/new"
                                    className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-brand-500 to-violet-600 text-white text-sm font-medium hover:shadow-glow-brand transition-shadow"
                                >
                                    <Plus className="h-4 w-4" />
                                    New Case
                                </Link>
                            </div>
                        )}
                    </div>
                </Reveal>
            </div>

            {/* Development progress */}
            <Reveal delay={0.2}>
                <div className="card-glass rounded-xl p-6">
                    <div className="flex items-center gap-2 mb-6">
                        <TrendingUp className="h-4 w-4 text-amber-400" />
                        <h2 className="font-display font-semibold text-white">Development Progress</h2>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[
                            { phase: 'Day 1-2', name: 'Foundation', status: 'complete' },
                            { phase: 'Day 3-4', name: 'AI Core', status: 'complete' },
                            { phase: 'Day 5', name: 'Dashboard', status: 'active' },
                            { phase: 'Day 6-7', name: 'Launch', status: 'upcoming' },
                        ].map((item) => (
                            <div
                                key={item.phase}
                                className={`p-4 rounded-xl border transition-all duration-200 ${
                                    item.status === 'complete'
                                        ? 'bg-emerald-400/5 border-emerald-400/20'
                                        : item.status === 'active'
                                            ? 'bg-brand-400/5 border-brand-400/30 ring-1 ring-brand-400/20'
                                            : 'bg-white/[0.02] border-white/10'
                                }`}
                            >
                                <p className={`text-xs font-medium ${
                                    item.status === 'complete' ? 'text-emerald-400' :
                                    item.status === 'active' ? 'text-brand-400' : 'text-white/30'
                                }`}>
                                    {item.phase}
                                </p>
                                <p className={`text-lg font-semibold mt-1 ${
                                    item.status === 'complete' ? 'text-emerald-300' :
                                    item.status === 'active' ? 'text-white' : 'text-white/50'
                                }`}>
                                    {item.name}
                                </p>
                                <p className={`text-xs mt-1 ${
                                    item.status === 'complete' ? 'text-emerald-400/70' :
                                    item.status === 'active' ? 'text-brand-400/70 animate-pulse' : 'text-white/25'
                                }`}>
                                    {item.status === 'complete' ? 'Complete' : item.status === 'active' ? 'In Progress' : 'Upcoming'}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </Reveal>
        </div>
    );
}
