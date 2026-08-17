import { useState, useCallback } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { Search, Loader2, AlertCircle, AlertTriangle, Frown } from 'lucide-react';
import { useSearchByPhoto } from '../hooks/useSearch';
import { EASE, Stagger, StaggerItem } from '../components/motion/primitives';

interface SearchResult {
    record_id: string;
    person_id: string;
    age: number;
    capture_year?: number;
    dataset: string;
    photo_path: string;
    face_similarity: number;
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

export function SearchPage() {
    const [file, setFile] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [topK, setTopK] = useState(20);
    const [minSimilarity, setMinSimilarity] = useState(0.3);
    const reducedMotion = useReducedMotion();

    const searchMutation = useSearchByPhoto();

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selected = e.target.files?.[0];
        if (!selected) return;
        setFile(selected);
        const url = URL.createObjectURL(selected);
        setPreviewUrl(url);
    };

    const handleSearch = useCallback(async () => {
        if (!file) return;
        await searchMutation.mutate({
            file,
            params: { top_k: topK, min_similarity: minSimilarity },
        });
    }, [file, topK, minSimilarity, searchMutation]);

    const results = searchMutation.data?.results || [];

    return (
        <div className="space-y-6 relative">
            <div className="absolute top-20 left-1/4 w-80 h-80 bg-brand-500/10 rounded-full blur-[80px] pointer-events-none" />
            <div className="absolute bottom-20 right-1/4 w-64 h-64 bg-cyan-500/10 rounded-full blur-[60px] pointer-events-none" />

            <div className="relative">
                <h1 className="text-2xl lg:text-3xl font-display font-bold text-white tracking-tight">Quick Search</h1>
                <p className="mt-1 text-white/50 text-sm">Search the face database without creating a case</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 relative">
                <motion.div
                    className="lg:col-span-1"
                    initial={reducedMotion ? false : { opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, ease: EASE }}
                >
                    <div className="card-glass rounded-2xl p-6 space-y-5">
                        <h2 className="font-display font-semibold text-white">Upload Photo</h2>

                        <label
                            className={`relative flex flex-col items-center justify-center border-2 border-dashed rounded-2xl p-8 cursor-pointer transition-colors ${
                                previewUrl ? 'border-brand-500/40 bg-brand-500/5' : 'border-white/10 hover:border-white/20'
                            }`}
                        >
                            <input
                                type="file"
                                accept="image/jpeg,image/png,image/webp"
                                onChange={handleFileChange}
                                className="sr-only"
                            />
                            {previewUrl ? (
                                <>
                                    <img
                                        src={previewUrl}
                                        alt="Upload preview"
                                        className="h-32 w-32 object-cover rounded-xl mb-4"
                                    />
                                    <p className="text-sm text-white/60 font-medium">Click to change photo</p>
                                </>
                            ) : (
                                <>
                                    <div className="h-14 w-14 rounded-2xl bg-white/5 flex items-center justify-center mb-4">
                                        <Search className="h-6 w-6 text-white/40" />
                                    </div>
                                    <p className="text-sm font-medium text-white/70">Drop an image here</p>
                                    <p className="text-xs text-white/40 mt-1">or click to browse</p>
                                    <p className="text-xs text-white/30 mt-3">JPG, PNG, WEBP · max 10MB</p>
                                </>
                            )}
                        </label>

                        <div className="space-y-5">
                            <div>
                                <label htmlFor="topK" className="block text-sm font-medium text-white/70 mb-2">
                                    Number of Results: <span className="text-brand-400">{topK}</span>
                                </label>
                                <input
                                    id="topK"
                                    type="range"
                                    min={5}
                                    max={50}
                                    value={topK}
                                    onChange={(e) => setTopK(Number(e.target.value))}
                                    className="w-full"
                                />
                                <div className="flex justify-between text-xs text-white/40 mt-1.5">
                                    <span>5</span>
                                    <span>50</span>
                                </div>
                            </div>

                            <div>
                                <label htmlFor="minSimilarity" className="block text-sm font-medium text-white/70 mb-2">
                                    Minimum Similarity: <span className="text-brand-400">{(minSimilarity * 100).toFixed(0)}%</span>
                                </label>
                                <input
                                    id="minSimilarity"
                                    type="range"
                                    min={0}
                                    max={100}
                                    step={5}
                                    value={minSimilarity * 100}
                                    onChange={(e) => setMinSimilarity(Number(e.target.value) / 100)}
                                    className="w-full"
                                />
                                <div className="flex justify-between text-xs text-white/40 mt-1.5">
                                    <span>0%</span>
                                    <span>100%</span>
                                </div>
                            </div>
                        </div>

                        <button
                            onClick={handleSearch}
                            disabled={!file || searchMutation.isPending}
                            className="w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-brand-500 to-violet-600 text-white font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-glow-brand hover:-translate-y-0.5 transition-all duration-200"
                        >
                            {searchMutation.isPending ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                                <Search className="h-4 w-4" />
                            )}
                            {searchMutation.isPending ? 'Searching...' : 'Search Database'}
                        </button>
                    </div>
                </motion.div>

                <motion.div
                    className="lg:col-span-2"
                    initial={reducedMotion ? false : { opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, ease: EASE, delay: 0.1 }}
                >
                    <div className="card-glass rounded-2xl p-6 h-full">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="font-display font-semibold text-white">Search Results</h2>
                            {searchMutation.data && (
                                <span className="text-sm text-white/40">
                                    {searchMutation.data.total_records} records scanned
                                </span>
                            )}
                        </div>

                        {searchMutation.isPending && (
                            <div className="flex flex-col items-center justify-center py-16">
                                <div className="relative">
                                    <Loader2 className="h-10 w-10 text-brand-400 animate-spin" />
                                    <div className="absolute inset-0 h-10 w-10 rounded-full bg-brand-400/20 blur-xl animate-pulse" />
                                </div>
                                <p className="mt-6 text-white/60 font-medium">Searching database...</p>
                                <p className="mt-1 text-sm text-white/40">AI is analyzing facial features</p>
                            </div>
                        )}

                        {searchMutation.isError && (
                            <div className="flex items-center gap-3 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl" role="alert">
                                <AlertCircle className="h-5 w-5 text-rose-400 flex-shrink-0" />
                                <div>
                                    <p className="text-sm font-medium text-rose-300">Search failed</p>
                                    <p className="text-sm text-rose-300/70">
                                        {searchMutation.error instanceof Error ? searchMutation.error.message : 'An error occurred'}
                                    </p>
                                </div>
                            </div>
                        )}

                        {searchMutation.data?.quality_warning && (
                            <div className="flex items-start gap-3 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl mb-4" role="alert">
                                <AlertTriangle className="h-5 w-5 text-amber-400 flex-shrink-0 mt-0.5" />
                                <div>
                                    <p className="text-sm font-medium text-amber-300">Low quality face detected</p>
                                    <p className="text-sm text-amber-300/70">{searchMutation.data.quality_warning}</p>
                                </div>
                            </div>
                        )}

                        {!searchMutation.isPending && !searchMutation.isError && results.length === 0 && !file && (
                            <div className="flex flex-col items-center justify-center py-16 text-center">
                                <div className="h-14 w-14 rounded-2xl bg-white/5 flex items-center justify-center mb-4">
                                    <Search className="h-6 w-6 text-white/30" />
                                </div>
                                <h3 className="text-lg font-semibold text-white/80">No search performed</h3>
                                <p className="mt-2 text-white/40 text-sm">Upload a photo and click search to find matches</p>
                            </div>
                        )}

                        {!searchMutation.isPending && !searchMutation.isError && results.length === 0 && file && (
                            <div className="flex flex-col items-center justify-center py-16 text-center">
                                <div className="h-14 w-14 rounded-2xl bg-white/5 flex items-center justify-center mb-4">
                                    <Frown className="h-6 w-6 text-amber-400/60" />
                                </div>
                                <h3 className="text-lg font-semibold text-white/80">No matches found</h3>
                                <p className="mt-2 text-white/40 text-sm">Try lowering the similarity threshold</p>
                            </div>
                        )}

                        {results.length > 0 && (
                            <Stagger className="grid grid-cols-1 md:grid-cols-2 gap-3" staggerDelay={0.05}>
                                {results.map((result, index) => (
                                    <StaggerItem key={result.record_id}>
                                        <ResultCard result={result} rank={index + 1} />
                                    </StaggerItem>
                                ))}
                            </Stagger>
                        )}
                    </div>
                </motion.div>
            </div>
        </div>
    );
}

function ResultCard({ result, rank }: { result: SearchResult; rank: number }) {
    const similarity = result.face_similarity;
    const color = getSimilarityColor(similarity);
    const barColor = getSimilarityBar(similarity);
    const label = getSimilarityLabel(similarity);

    return (
        <div className="group flex gap-4 p-4 card-glass rounded-xl hover:bg-white/[0.05] hover:border-white/15 transition-all duration-200">
            <div className="flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden bg-white/5 relative">
                <img
                    src={result.photo_path}
                    alt={`Candidate ${result.person_id}`}
                    className="w-full h-full object-cover"
                />
                <div className="absolute top-1.5 left-1.5 bg-black/70 text-brand-400 text-xs font-bold px-2 py-0.5 rounded-md border border-brand-400/30">
                    #{rank}
                </div>
            </div>

            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                    <span className="font-semibold text-white text-sm group-hover:text-brand-300 transition-colors truncate">
                        {result.person_id}
                    </span>
                    <span className="px-2 py-0.5 text-xs bg-white/10 text-white/60 rounded-md border border-white/10 flex-shrink-0">
                        {result.dataset}
                    </span>
                </div>

                <div className="mb-2">
                    <div className="flex items-center justify-between text-xs mb-1">
                        <span className={`font-semibold ${color}`}>{label}</span>
                        <span className="text-white/40 font-mono">{(similarity * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                        <motion.div
                            className={`h-full rounded-full bg-gradient-to-r ${barColor}`}
                            initial={{ width: 0 }}
                            animate={{ width: `${similarity * 100}%` }}
                            transition={{ duration: 0.8, ease: EASE, delay: 0.2 }}
                        />
                    </div>
                </div>

                <div className="text-xs text-white/40 space-y-0.5">
                    <p>Age: {result.age}</p>
                    {result.capture_year && <p>Year: {result.capture_year}</p>}
                </div>
            </div>
        </div>
    );
}
