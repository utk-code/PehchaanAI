import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, useReducedMotion } from 'framer-motion';
import { AlertCircle, Loader2, Eye, EyeOff, CheckCircle2, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { EASE } from '../components/motion/primitives';

export function RegisterPage() {
    const navigate = useNavigate();
    const { register } = useAuth();
    const reducedMotion = useReducedMotion();
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const passwordsMatch = password === confirmPassword;
    const passwordLongEnough = password.length >= 8;

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setError(null);

        if (!passwordsMatch) {
            setError('Passwords do not match');
            return;
        }

        if (!passwordLongEnough) {
            setError('Password must be at least 8 characters');
            return;
        }

        setIsLoading(true);

        try {
            await register({ email, full_name: fullName, password });
            navigate('/dashboard', { replace: true });
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to create account';
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

    const inputClass =
        'w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-brand-500/40 focus:border-brand-500/50 transition-all';

    return (
        <div className="min-h-screen bg-atmosphere relative flex items-center justify-center p-4 overflow-hidden">
            <div className="absolute top-20 left-10 w-72 h-72 bg-brand-500/10 rounded-full blur-3xl animate-float" />
            <div className="absolute bottom-20 right-10 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-float-slow" />

            <motion.div
                className="w-full max-w-md relative z-10"
                {...fadeUp(0)}
            >
                <div className="text-center mb-8">
                    <motion.div
                        className="inline-flex items-center gap-3 mb-4"
                        {...fadeUp(0.1)}
                    >
                        <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center shadow-glow-brand">
                            <ShieldCheck className="h-6 w-6 text-white" />
                        </div>
                    </motion.div>
                    <motion.h1
                        className="text-3xl font-display font-bold text-white tracking-tight"
                        {...fadeUp(0.15)}
                    >
                        Create Account
                    </motion.h1>
                    <motion.p
                        className="mt-2 text-white/50"
                        {...fadeUp(0.2)}
                    >
                        Join the investigation workspace
                    </motion.p>
                </div>

                <motion.div
                    className="card-glass-elevated rounded-2xl p-8"
                    {...fadeUp(0.25)}
                >
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {error && (
                            <div className="flex items-start gap-3 p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl" role="alert">
                                <AlertCircle className="h-5 w-5 text-rose-400 flex-shrink-0 mt-0.5" />
                                <p className="text-sm text-rose-300">{error}</p>
                            </div>
                        )}

                        <div className="space-y-2">
                            <label htmlFor="fullName" className="block text-sm font-medium text-white/70">
                                Full Name
                            </label>
                            <input
                                id="fullName"
                                type="text"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                placeholder="John Doe"
                                required
                                autoComplete="name"
                                disabled={isLoading}
                                className={inputClass}
                            />
                        </div>

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
                                className={inputClass}
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
                                    placeholder="Create a strong password"
                                    required
                                    autoComplete="new-password"
                                    disabled={isLoading}
                                    className={`${inputClass} pr-12`}
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
                            {password && passwordLongEnough && (
                                <div className="flex items-center gap-1.5 mt-1.5 text-emerald-400">
                                    <CheckCircle2 className="h-4 w-4" />
                                    <span className="text-xs">Password is strong enough</span>
                                </div>
                            )}
                            {password && !passwordLongEnough && (
                                <p className="text-xs text-amber-400 mt-1.5">Password must be at least 8 characters</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <label htmlFor="confirmPassword" className="block text-sm font-medium text-white/70">
                                Confirm Password
                            </label>
                            <input
                                id="confirmPassword"
                                type={showPassword ? 'text' : 'password'}
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                placeholder="Confirm your password"
                                required
                                autoComplete="new-password"
                                disabled={isLoading}
                                className={inputClass}
                            />
                            {confirmPassword && !passwordsMatch && (
                                <p className="text-xs text-rose-400 mt-1.5">Passwords do not match</p>
                            )}
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading || !passwordsMatch || !passwordLongEnough}
                            className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-brand-500 to-violet-600 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 hover:shadow-glow-brand hover:-translate-y-0.5 transition-all duration-200"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="h-5 w-5 animate-spin" />
                                    Creating account...
                                </>
                            ) : (
                                'Create Account'
                            )}
                        </button>
                    </form>
                </motion.div>

                <motion.p
                    className="mt-6 text-center text-white/50 text-sm"
                    {...fadeUp(0.3)}
                >
                    Already have an account?{' '}
                    <Link to="/login" className="text-brand-400 hover:text-brand-300 font-medium transition-colors">
                        Sign in
                    </Link>
                </motion.p>
            </motion.div>
        </div>
    );
}
