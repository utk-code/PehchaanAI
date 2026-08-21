import { Link } from 'react-router-dom';
import { motion, useReducedMotion } from 'framer-motion';
import { Plus, Search, AlertCircle, Clock, Users, MapPin, Calendar } from 'lucide-react';
import { useState } from 'react';
import { useCases } from '../hooks/useCases';
import { EASE, Stagger, StaggerItem } from '../components/motion/primitives';

function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    });
}

export function CaseListPage() {
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'archived'>('all');
    const reducedMotion = useReducedMotion();

    const { data: cases, isLoading, error, refetch } = useCases({
        status: statusFilter === 'all' ? undefined : statusFilter,
        limit: 100,
    });

    const filteredCases = cases?.filter((c) => {
        const matchesQuery =
            !searchQuery ||
            (c.query_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
            c.id.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesQuery;
    });

    const statusTabs = [
        { value: 'all' as const, label: 'All' },
        { value: 'active' as const, label: 'Active' },
        { value: 'archived' as const, label: 'Archived' },
    ];

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <span className="mono-label">Case Registry</span>
                    </div>
                    <h1 className="text-3xl lg:text-4xl font-display font-bold text-white tracking-tight leading-none">Cases</h1>
                    <p className="mt-1 text-white/50 text-sm">Manage your investigation cases</p>
                </div>
                <Link
                    to="/cases/new"
                    className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-brand-500 to-violet-600 text-white text-sm font-medium hover:shadow-glow-brand hover:-translate-y-0.5 transition-all duration-200"
                >
                    <Plus className="h-4 w-4" />
                    New Case
                </Link>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-white/30" />
                    <input
                        type="text"
                        placeholder="Search cases by name or ID..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-brand-500/40 focus:border-brand-500/50 transition-all text-sm"
                    />
                </div>
                <div className="flex items-center gap-1 bg-white/[0.04] border border-white/10 rounded-lg p-1">
                    {statusTabs.map((tab) => (
                        <button
                            key={tab.value}
                            onClick={() => setStatusFilter(tab.value)}
                            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                                statusFilter === tab.value
                                    ? 'bg-gradient-to-r from-brand-500 to-violet-600 text-white shadow-glow-brand'
                                    : 'text-white/50 hover:text-white hover:bg-white/5'
                            }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>
            </div>

            {isLoading ? (
                <div className="space-y-3">
                    {[1, 2, 3, 4, 5].map((i) => (
                        <div key={i} className="h-20 bg-white/[0.03] border border-white/5 rounded-xl animate-pulse" />
                    ))}
                </div>
            ) : error ? (
                <div className="flex flex-col items-center justify-center py-16 text-center card-glass rounded-xl">
                    <AlertCircle className="h-12 w-12 text-rose-400/50" />
                    <h3 className="mt-4 text-lg font-semibold text-white/80">Failed to load cases</h3>
                    <p className="mt-2 text-white/40 text-sm">{error instanceof Error ? error.message : 'An unexpected error occurred'}</p>
                    <button
                        onClick={() => refetch()}
                        className="mt-5 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-sm text-white/80 hover:bg-white/10 transition-colors"
                    >
                        Try Again
                    </button>
                </div>
            ) : !filteredCases || filteredCases.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 text-center card-glass rounded-xl">
                    <div className="h-14 w-14 rounded-xl bg-white/5 flex items-center justify-center mb-4">
                        <Users className="h-6 w-6 text-white/30" />
                    </div>
                    <h3 className="text-lg font-semibold text-white/80">
                        {searchQuery || statusFilter !== 'all' ? 'No matching cases' : 'No cases yet'}
                    </h3>
                    <p className="mt-2 text-white/40 text-sm">
                        {searchQuery || statusFilter !== 'all'
                            ? 'Try adjusting your search or filters'
                            : 'Get started by creating your first case'}
                    </p>
                    {!searchQuery && statusFilter === 'all' && (
                        <Link
                            to="/cases/new"
                            className="mt-5 inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-brand-500 to-violet-600 text-white text-sm font-medium hover:shadow-glow-brand transition-shadow"
                        >
                            <Plus className="h-4 w-4" />
                            Create First Case
                        </Link>
                    )}
                </div>
            ) : (
                <Stagger className="space-y-3" staggerDelay={0.04}>
                    {filteredCases.map((caseItem) => (
                        <StaggerItem key={caseItem.id}>
                            <Link
                                to={`/cases/${caseItem.id}`}
                                className="group card-glass rounded-xl p-5 block tick-corners hover:bg-white/[0.05] hover:border-white/15 hover:-translate-y-0.5 transition-all duration-200"
                            >
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-3">
                                            <h3 className="text-lg font-semibold text-white truncate group-hover:text-brand-300 transition-colors">
                                                {caseItem.query_name || 'Unnamed Case'}
                                            </h3>
                                            <span
                                                className={`px-2.5 py-0.5 text-xs font-medium rounded-full flex-shrink-0 ${
                                                    caseItem.status === 'active'
                                                        ? 'bg-emerald-400/10 text-emerald-300 border border-emerald-400/20'
                                                        : 'bg-white/5 text-white/50 border border-white/10'
                                                }`}
                                            >
                                                {caseItem.status}
                                            </span>
                                        </div>

                                        <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-white/40">
                                            {caseItem.query_age !== null && caseItem.query_age !== undefined && (
                                                <span className="flex items-center gap-1.5">
                                                    <Users size={14} />
                                                    {caseItem.query_age} years old
                                                </span>
                                            )}
                                            {caseItem.query_location && (
                                                <span className="flex items-center gap-1.5">
                                                    <MapPin size={14} />
                                                    {caseItem.query_location}
                                                </span>
                                            )}
                                            {caseItem.query_date && (
                                                <span className="flex items-center gap-1.5">
                                                    <Calendar size={14} />
                                                    Photo: {formatDate(caseItem.query_date)}
                                                </span>
                                            )}
                                            <span className="flex items-center gap-1.5">
                                                <Clock size={14} />
                                                Created: {formatDate(caseItem.created_at)}
                                            </span>
                                        </div>
                                    </div>

                                    <div className="flex-shrink-0 text-right">
                                        <span className="text-xs font-mono text-white/25">
                                            #{caseItem.id.slice(0, 8)}
                                        </span>
                                    </div>
                                </div>
                            </Link>
                        </StaggerItem>
                    ))}
                </Stagger>
            )}
        </div>
    );
}
