import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { motion, useReducedMotion } from 'framer-motion';
import {
    ArrowLeft,
    Search,
    User,
    Calendar,
    MapPin,
    AlertCircle,
    Loader2,
    FileText,
    ChevronDown,
    ChevronUp,
} from 'lucide-react';
import { useCase } from '../../hooks/useCases';
import { useSearchByCase } from '../../hooks/useSearch';
import { EASE } from '../motion/primitives';

function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    });
}

function getSimilarityColor(similarity: number): string {
    if (similarity >= 0.8) return 'text-emerald-400';
    if (similarity >= 0.6) return 'text-brand-400';
    if (similarity >= 0.4) return 'text-amber-400';
    return 'text-rose-400';
}

function getSimilarityBar(similarity: number): string {
    if (similarity >= 0.8) return 'from-emerald-400 to-teal-400';
    if (similarity >= 0.6) return 'from-brand-400 to-violet-500';
    if (similarity >= 0.4) return 'from-amber-400 to-orange-400';
    return 'from-rose-400 to-pink-500';
}

function getSimilarityLabel(similarity: number): string {
    if (similarity >= 0.8) return 'Very High';
    if (similarity >= 0.6) return 'High';
    if (similarity >= 0.4) return 'Medium';
    return 'Low';
}

export function CaseDetail() {
    const { caseId } = useParams<{ caseId: string }>();
    const navigate = useNavigate();
    const reducedMotion = useReducedMotion();
    const [showAllResults, setShowAllResults] = useState(false);
    const [expandedResult, setExpandedResult] = useState<string | null>(null);

    const { data: caseData, isLoading: caseLoading, error: caseError } = useCase(caseId!);
    const {
        data: searchData,
        isLoading: searchLoading,
        error: searchError,
        refetch: refetchSearch,
    } = useSearchByCase(caseId!, { top_k: 20, min_similarity: 0.3 });

    if (caseLoading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="relative">
                    <Loader2 className="h-10 w-10 text-brand-400 animate-spin" />
                    <div className="absolute inset-0 h-10 w-10 rounded-full bg-brand-400/20 blur-xl animate-pulse" />
                </div>
            </div>
        );
    }

    if (caseError || !caseData) {
        return (
            <div className="card-glass rounded-xl p-8">
                <div className="flex flex-col items-center justify-center py-12 text-center">
                    <AlertCircle className="h-12 w-12 text-rose-400/50" />
                    <h3 className="mt-4 text-lg font-semibold text-white/80">Case not found</h3>
                    <p className="mt-2 text-white/40 text-sm">
                        {caseError instanceof Error ? caseError.message : 'The requested case could not be found.'}
                    </p>
                    <button
                        onClick={() => navigate('/cases')}
                        className="mt-5 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-sm text-white/80 hover:bg-white/10 transition-colors inline-flex items-center gap-2"
                    >
                        <ArrowLeft className="h-4 w-4" />
                        Back to Cases
                    </button>
                </div>
            </div>
        );
    }

    const results = searchData?.results || [];
    const displayResults = showAllResults ? results : results.slice(0, 5);

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                <div className="flex-1">
                    <Link
                        to="/cases"
                        className="inline-flex items-center gap-1.5 text-sm text-white/50 hover:text-white/80 transition-colors mb-2"
                    >
                        <ArrowLeft className="h-4 w-4" />
                        Back to Cases
                    </Link>
                    <div className="mono-label mb-1">Case Dossier / {caseData.id.slice(0, 8).toUpperCase()}</div>
                    <div className="flex items-center gap-3">
                        <h1 className="text-2xl lg:text-3xl font-display font-bold text-white tracking-tight">
                            {caseData.query_name || 'Unnamed Case'}
                        </h1>
                        <span
                            className={`px-3 py-1 text-sm font-medium rounded-full ${
                                caseData.status === 'active'
                                    ? 'bg-emerald-400/10 text-emerald-300 border border-emerald-400/20'
                                    : 'bg-white/5 text-white/50 border border-white/10'
                            }`}
                        >
                            {caseData.status}
                        </span>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={() => refetchSearch()}
                        disabled={searchLoading}
                        className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white/80 text-sm font-medium hover:bg-white/10 disabled:opacity-50 transition-colors"
                    >
                        <Search className="h-4 w-4" />
                        Re-run Search
                    </button>
                    <button className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white/80 text-sm font-medium hover:bg-white/10 transition-colors">
                        <FileText className="h-4 w-4" />
                        Generate Report
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <motion.div
                    className="lg:col-span-2"
                    initial={reducedMotion ? false : { opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, ease: EASE }}
                >
                    <div className="card-glass rounded-xl p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="font-display font-semibold text-white">Search Results</h2>
                            {searchData && (
                                <span className="text-sm text-white/40">
                                    {searchData.total_records} records scanned
                                </span>
                            )}
                        </div>

                        {searchLoading && (
                            <div className="flex items-center justify-center py-12">
                                <Loader2 className="h-8 w-8 text-brand-400 animate-spin" />
                            </div>
                        )}

                        {searchError && (
                            <div className="flex items-center gap-3 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl" role="alert">
                                <AlertCircle className="h-5 w-5 text-rose-400 flex-shrink-0" />
                                <div>
                                    <p className="text-sm font-medium text-rose-300">Search failed</p>
                                    <p className="text-sm text-rose-300/70">
                                        {searchError instanceof Error ? searchError.message : 'An unexpected error occurred'}
                                    </p>
                                </div>
                            </div>
                        )}

                        {!searchLoading && !searchError && results.length === 0 && (
                            <div className="flex flex-col items-center justify-center py-12 text-center">
                                <div className="h-14 w-14 rounded-xl bg-white/5 flex items-center justify-center mb-4">
                                    <Search className="h-6 w-6 text-white/30" />
                                </div>
                                <h3 className="text-lg font-semibold text-white/80">No matches found</h3>
                                <p className="mt-2 text-white/40 text-sm max-w-md">
                                    No candidates matched above the similarity threshold. Try lowering the threshold or
                                    adding more reference photos to the database.
                                </p>
                            </div>
                        )}

                        {!searchLoading && !searchError && results.length > 0 && (
                            <div className="space-y-3">
                                {displayResults.map((result, index) => (
                                    <CandidateCard
                                        key={result.record_id}
                                        result={result}
                                        rank={index + 1}
                                        isExpanded={expandedResult === result.record_id}
                                        onToggle={() => setExpandedResult(expandedResult === result.record_id ? null : result.record_id)}
                                    />
                                ))}

                                {results.length > 5 && (
                                    <div className="text-center pt-2">
                                        <button
                                            onClick={() => setShowAllResults(!showAllResults)}
                                            className="inline-flex items-center gap-1.5 px-4 py-2 text-sm text-brand-400 hover:text-brand-300 transition-colors"
                                        >
                                            {showAllResults ? (
                                                <>
                                                    <ChevronUp className="h-4 w-4" />
                                                    Show Less
                                                </>
                                            ) : (
                                                <>
                                                    Show All {results.length} Results
                                                    <ChevronDown className="h-4 w-4" />
                                                </>
                                            )}
                                        </button>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </motion.div>

                <motion.div
                    initial={reducedMotion ? false : { opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, ease: EASE, delay: 0.1 }}
                >
                    <div className="card-glass rounded-xl p-6">
                        <h2 className="font-display font-semibold text-white mb-4">Query Image</h2>

                        <div className="aspect-square bg-white/5 rounded-xl overflow-hidden flex items-center justify-center mb-4">
                            {caseData.photo_path ? (
                                <img
                                    src={caseData.photo_path}
                                    alt={`Query photo for ${caseData.query_name || 'case'}`}
                                    className="w-full h-full object-cover"
                                />
                            ) : (
                                <div className="text-white/30 text-sm">No image</div>
                            )}
                        </div>

                        <div className="space-y-3 text-sm">
                            <div className="flex items-center gap-2 text-white/50">
                                <User size={16} className="text-brand-400" />
                                <span>
                                    <span className="text-white/30">Name:</span> {caseData.query_name || 'Not provided'}
                                </span>
                            </div>
                            {caseData.query_age !== null && caseData.query_age !== undefined && (
                                <div className="flex items-center gap-2 text-white/50">
                                    <User size={16} className="text-brand-400" />
                                    <span>
                                        <span className="text-white/30">Age:</span> {caseData.query_age} years
                                    </span>
                                </div>
                            )}
                            {caseData.query_date && (
                                <div className="flex items-center gap-2 text-white/50">
                                    <Calendar size={16} className="text-brand-400" />
                                    <span>
                                        <span className="text-white/30">Photo Date:</span> {formatDate(caseData.query_date)}
                                    </span>
                                </div>
                            )}
                            {caseData.query_location && (
                                <div className="flex items-center gap-2 text-white/50">
                                    <MapPin size={16} className="text-brand-400" />
                                    <span>
                                        <span className="text-white/30">Location:</span> {caseData.query_location}
                                    </span>
                                </div>
                            )}
                            <div className="flex items-center gap-2 text-white/50">
                                <Calendar size={16} className="text-brand-400" />
                                <span>
                                    <span className="text-white/30">Case Created:</span> {formatDate(caseData.created_at)}
                                </span>
                            </div>
                        </div>

                        {caseData.notes && (
                            <div className="mt-4 p-4 bg-white/5 rounded-xl">
                                <p className="text-sm font-medium text-white/80 mb-1">Notes</p>
                                <p className="text-sm text-white/50 whitespace-pre-wrap">{caseData.notes}</p>
                            </div>
                        )}
                    </div>
                </motion.div>
            </div>
        </div>
    );
}

interface CandidateCardProps {
    result: {
        record_id: string;
        person_id: string;
        age: number;
        capture_year?: number;
        dataset: string;
        photo_path: string;
        face_similarity: number;
    };
    rank: number;
    isExpanded: boolean;
    onToggle: () => void;
}

function CandidateCard({ result, rank, isExpanded, onToggle }: CandidateCardProps) {
    const similarity = result.face_similarity;
    const color = getSimilarityColor(similarity);
    const barColor = getSimilarityBar(similarity);
    const label = getSimilarityLabel(similarity);
    const reducedMotion = useReducedMotion();

    return (
        <div className="card-glass rounded-xl overflow-hidden transition-all duration-200 hover:bg-white/[0.05]">
            <div className="p-4">
                <div className="flex gap-4">
                    <div className="flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden bg-white/5 relative">
                        <img
                            src={result.photo_path}
                            alt={`Candidate ${result.person_id}`}
                            className="w-full h-full object-cover"
                        />
                        <div className="absolute top-1 left-1 bg-black/70 text-brand-400 text-xs font-bold px-1.5 py-0.5 rounded">
                            #{rank}
                        </div>
                    </div>

                    <div className="flex-1 min-w-0 flex flex-col justify-between">
                        <div>
                            <div className="flex items-center gap-3">
                                <h4 className="font-semibold text-white truncate">Person: {result.person_id}</h4>
                                <span className="px-2 py-0.5 text-xs font-medium bg-white/10 text-white/60 rounded border border-white/10">
                                    {result.dataset}
                                </span>
                            </div>
                            <div className="mt-1 flex flex-wrap gap-4 text-sm text-white/40">
                                <span>Age: <strong className="text-white/70">{result.age}</strong></span>
                                {result.capture_year && <span>Year: <strong className="text-white/70">{result.capture_year}</strong></span>}
                            </div>
                        </div>

                        <div className="flex items-center justify-between pt-2">
                            <div className="flex-1 mr-4">
                                <div className="flex items-center justify-between text-xs mb-1">
                                    <span className={`font-semibold ${color}`}>{label} Match</span>
                                    <span className="text-white/40 font-mono">{(similarity * 100).toFixed(1)}%</span>
                                </div>
                                <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                                    <motion.div
                                        className={`h-full rounded-full bg-gradient-to-r ${barColor}`}
                                        initial={reducedMotion ? false : { width: 0 }}
                                        animate={{ width: `${similarity * 100}%` }}
                                        transition={{ duration: 0.8, ease: EASE }}
                                    />
                                </div>
                            </div>
                            <button
                                onClick={onToggle}
                                className="flex-shrink-0 p-2 text-white/40 hover:text-white rounded-lg hover:bg-white/5"
                                aria-expanded={isExpanded}
                                aria-label={isExpanded ? 'Collapse details' : 'Expand details'}
                            >
                                {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                            </button>
                        </div>
                    </div>
                </div>

                {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-white/10">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                            <div className="bg-white/5 p-3 rounded-lg">
                                <p className="text-white/40 text-xs">Person ID</p>
                                <p className="font-mono font-medium text-white/80 mt-0.5">{result.person_id}</p>
                            </div>
                            <div className="bg-white/5 p-3 rounded-lg">
                                <p className="text-white/40 text-xs">Age</p>
                                <p className="font-medium text-white/80 mt-0.5">{result.age}</p>
                            </div>
                            <div className="bg-white/5 p-3 rounded-lg">
                                <p className="text-white/40 text-xs">Capture Year</p>
                                <p className="font-medium text-white/80 mt-0.5">{result.capture_year || 'Unknown'}</p>
                            </div>
                            <div className="bg-white/5 p-3 rounded-lg">
                                <p className="text-white/40 text-xs">Dataset</p>
                                <p className="font-medium text-white/80 mt-0.5">{result.dataset}</p>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
