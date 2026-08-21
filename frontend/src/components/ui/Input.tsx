/** Input UI Component - Maximalist Design with Animated Focus States */

import { InputHTMLAttributes, forwardRef } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
    ({ className = '', label, error, helperText, id, ...props }, ref) => {
        const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

        return (
            <div className="w-full">
                {label && (
                    <label htmlFor={inputId} className="block text-sm font-medium text-white/70 mb-2">
                        {label}
                    </label>
                )}
                <div className="relative group">
                    <input
                        ref={ref}
                        id={inputId}
                        className={`
                            w-full px-4 py-3 
                            bg-white/5 
                            text-white 
                            border rounded-xl
                            placeholder:text-white/30
                            transition-all duration-200
                            focus:outline-none focus:ring-2 focus:ring-offset-0
                            disabled:bg-white/[0.02] disabled:text-white/30 disabled:cursor-not-allowed
                            backdrop-blur-sm
                            ${error
                                ? 'border-rose-400/50 focus:ring-rose-400/30 focus:border-rose-400'
                                : 'border-white/10 focus:ring-brand-500/30 focus:border-brand-500 hover:border-white/20'
                            }
                            ${className}
                        `}
                        aria-invalid={error ? 'true' : 'false'}
                        aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
                        {...props}
                    />
                    <div className="absolute inset-0 rounded-xl opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none bg-gradient-to-r from-brand-500/[0.12] via-transparent to-cyan-400/[0.08]" />
                </div>
                {error && (
                    <p id={`${inputId}-error`} className="mt-2 text-sm text-rose-400 flex items-center gap-1.5" role="alert">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-pulse" />
                        {error}
                    </p>
                )}
                {helperText && !error && (
                    <p id={`${inputId}-helper`} className="mt-2 text-sm text-white/40">
                        {helperText}
                    </p>
                )}
            </div>
        );
    }
);

Input.displayName = 'Input';
