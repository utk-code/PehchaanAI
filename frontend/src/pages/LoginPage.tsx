import { useState, FormEvent } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { motion, useReducedMotion } from 'framer-motion';
import { AlertCircle, Loader2, Eye, EyeOff, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { EASE } from '../components/motion/primitives';

export function LoginPage() {
    const navigate = useNavigate();
    const location = useLocation();
    const { login } = useAuth();
    const reducedMotion = useReducedMotion();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/dashboard';

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);

        try {
            await login({ username: email, password });
            navigate(from, { replace: true });
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to login';
            setError(message);
        } finally {
            setIsLoading(false);
        }
    };

    const fadeUp = (delay: number) =>
        reducedMotion ? {} : {
            initial: { opacity: 0, y: 16 },
            animate: { opacity: 1, y: 0 },
            transition: { duration: 0.6, ease: EASE, delay },
        };

    return (
        <div className="min-h-screen bg-atmosphere relative flex items-center justify-center p-4 overflow-hidden">
            <div className="grain" aria-hidden />
            <div className="absolute inset-0 bg-grid opacity-60" aria-hidden />
            <div className="absolute top-24 -left-24 w-96 h-96 rounded-full border border-brand-500/15 animate-float" />
            <div className="absolute -bottom-32 right-0 w-[520px] h-[520px] rounded-full border border-cyan-400/10 animate-float-slow" />
            <div className="absolute top-1/3 right-[12%] w-24 h-24 rounded-full border border-brand-500/25" />
            <div className="absolute bottom-[18%] left-[14%] w-2 h-2 bg-brand-500 rounded-full animate-pulse-ring" />

            <div className="absolute top-6 left-6 font-mono text-[10px] tracking-[0.3em] uppercase text-white/30 pointer-events-none">
                PCHN-2026 / Secure Channel
            </div>
            <div className="absolute top-6 right-6 flex items-center gap-2 font-mono text-[10px] tracking-[0.2em] uppercase text-white/30 pointer-events-none">
                <span className="beacon-dot" />
                System Online
            </div>

            <motion.div
                className="w-full max-w-lg relative z-10"
                {...fadeUp(0)}
            >
                <div className="text-center mb-8">
                    <motion.div
                        className="inline-flex items-center gap-3 mb-5"
                        {...fadeUp(0.1)}
                    >
                        <div className="relative">
                            <span className="absolute inset-0 rounded-xl bg-brand-500/40 animate-pulse-ring" />
                            <div className="relative h-14 w-14 rounded-xl bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center shadow-glow-brand">
                                <ShieldCheck className="h-7 w-7 text-white" />
                            </div>
                        </div>
                    </motion.div>
                    <motion.h1
                        className="text-4xl sm:text-5xl font-display font-bold text-white tracking-tight"
                        {...fadeUp(0.15)}
                    >
                        Pehchaan<span className="text-gradient">AI</span>
                    </motion.h1>
                    <motion.p
                        className="mt-3 font-mono text-[11px] tracking-[0.28em] uppercase text-white/45"
                        {...fadeUp(0.2)}
                    >
                        Sign in to the investigation workspace
                        <span className="terminal-caret" aria-hidden />
                    </motion.p>
                </div>

                <motion.div
                    className="card-glass-elevated rounded-xl p-8 tick-corners relative"
                    {...fadeUp(0.25)}
                >
                    <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-brand-500/0 via-brand-500/60 to-cyan-400/0" aria-hidden />
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {error && (
                            <motion.div
                                className="flex items-start gap-3 p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl"
                                role="alert"
                                initial={reducedMotion ? false : { opacity: 0, y: -8 }}
                                animate={{ opacity: 1, y: 0 }}
                            >
                                <AlertCircle className="h-5 w-5 text-rose-400 flex-shrink-0 mt-0.5" />
                                <p className="text-sm text-rose-300">{error}</p>
                            </motion.div>
                        )}

                        <div className="space-y-2">
                            <label htmlFor="email" className="block text-sm font-medium text-white/70">
                                Email
                            </label>
                            <input
                                id="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="you@example.com"
                                required
                                autoComplete="email"
                                disabled={isLoading}
                                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-brand-500/40 focus:border-brand-500/50 transition-all"
                            />
                        </div>

                        <div className="space-y-2">
                            <label htmlFor="password" className="block text-sm font-medium text-white/70">
                                Password
                            </label>
                            <div className="relative">
                                <input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Enter your password"
                                    required
                                    autoComplete="current-password"
                                    disabled={isLoading}
                                    className="w-full px-4 py-3 pr-12 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-brand-500/40 focus:border-brand-500/50 transition-all"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/70 transition-colors"
                                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                                >
                                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                                </button>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-brand-500 to-violet-600 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 hover:shadow-glow-brand hover:-translate-y-0.5 transition-all duration-200"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="h-5 w-5 animate-spin" />
                                    Signing in...
                                </>
                            ) : (
                                'Sign in'
                            )}
                        </button>
                    </form>
                </motion.div>

                <motion.p
                    className="mt-6 text-center text-white/50 text-sm"
                    {...fadeUp(0.3)}
                >
                    Don't have an account?{' '}
                    <Link
                        to="/register"
                        className="text-brand-400 hover:text-brand-300 font-medium transition-colors"
                    >
                        Create one
                    </Link>
                </motion.p>
            </motion.div>
        </div>
    );
}
