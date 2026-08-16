import { HTMLAttributes, forwardRef } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'outlined' | 'elevated' | 'glass';
    padding?: 'none' | 'sm' | 'md' | 'lg';
    hover?: boolean;
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
    ({ className = '', variant = 'glass', padding = 'md', hover = false, children, ...props }, ref) => {
        const variantStyles = {
            default: 'bg-white/5 border border-white/10',
            outlined: 'bg-transparent border border-white/15',
            elevated: 'card-glass-elevated',
            glass: 'card-glass',
        };

        const paddingStyles = {
            none: '',
            sm: 'p-4',
            md: 'p-6',
            lg: 'p-8',
        };

        return (
            <div
                ref={ref}
                className={`
                    ${variantStyles[variant]}
                    ${paddingStyles[padding]}
                    rounded-2xl
                    ${hover ? 'transition-all duration-200 hover:bg-white/[0.06] hover:border-white/20' : ''}
                    ${className}
                `}
                {...props}
            >
                {children}
            </div>
        );
    }
);

Card.displayName = 'Card';

export const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
    ({ className = '', children, ...props }, ref) => (
        <div ref={ref} className={`mb-4 ${className}`} {...props}>
            {children}
        </div>
    )
);

CardHeader.displayName = 'CardHeader';

export const CardTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>>(
    ({ className = '', children, ...props }, ref) => (
        <h3 ref={ref} className={`font-display font-semibold text-white ${className}`} {...props}>
            {children}
        </h3>
    )
);

CardTitle.displayName = 'CardTitle';

export const CardDescription = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLParagraphElement>>(
    ({ className = '', children, ...props }, ref) => (
        <p ref={ref} className={`mt-1 text-sm text-white/50 ${className}`} {...props}>
            {children}
        </p>
    )
);

CardDescription.displayName = 'CardDescription';

export const CardContent = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
    ({ className = '', children, ...props }, ref) => (
        <div ref={ref} className={className} {...props}>
            {children}
        </div>
    )
);

CardContent.displayName = 'CardContent';

export const CardFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
    ({ className = '', children, ...props }, ref) => (
        <div ref={ref} className={`mt-4 flex items-center gap-3 ${className}`} {...props}>
            {children}
        </div>
    )
);

CardFooter.displayName = 'CardFooter';
