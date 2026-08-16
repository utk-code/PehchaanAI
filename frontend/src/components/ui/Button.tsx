import { ButtonHTMLAttributes, forwardRef } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className = '', variant = 'primary', size = 'md', loading = false, disabled, children, ...props }, ref) => {
        const baseStyles = `
            inline-flex items-center justify-center font-medium rounded-xl
            transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-offset-0
            disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
            active:scale-[0.97]
        `;

        const variantStyles = {
            primary: `
                bg-gradient-to-r from-brand-500 to-violet-600
                text-white
                hover:shadow-glow-brand hover:-translate-y-0.5
                focus:ring-brand-500/50
            `,
            secondary: `
                bg-white/5
                text-white
                border border-white/15
                hover:bg-white/10 hover:border-white/25 hover:-translate-y-0.5
                focus:ring-white/40
            `,
            danger: `
                bg-gradient-to-r from-rose-500 to-pink-600
                text-white
                hover:-translate-y-0.5
                focus:ring-rose-500/50
            `,
            ghost: `
                bg-transparent
                text-white/60
                hover:text-white hover:bg-white/5
                focus:ring-white/30
            `,
        };

        const sizeStyles = {
            sm: 'px-3 py-1.5 text-sm gap-1.5',
            md: 'px-4 py-2.5 text-sm gap-2',
            lg: 'px-6 py-3 text-base gap-2.5',
        };

        return (
            <button
                ref={ref}
                className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
                disabled={disabled || loading}
                {...props}
            >
                {loading && (
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                        <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                            fill="none"
                        />
                        <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                        />
                    </svg>
                )}
                {children}
            </button>
        );
    }
);

Button.displayName = 'Button';
