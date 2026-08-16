/** ProgressBar UI Component with Animated Gradient Fill */

interface ProgressBarProps {
    value: number;
    max?: number;
    size?: 'sm' | 'md' | 'lg';
    color?: 'blue' | 'green' | 'amber' | 'red' | 'gradient';
    showLabel?: boolean;
    label?: string;
    className?: string;
}

export function ProgressBar({
    value,
    max = 100,
    size = 'md',
    color = 'gradient',
    showLabel = true,
    label,
    className = '',
}: ProgressBarProps) {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

    const sizeStyles = {
        sm: 'h-1.5',
        md: 'h-2.5',
        lg: 'h-4',
    };

    const colorStyles = {
        blue: 'bg-gradient-to-r from-brand-500 to-brand-400',
        green: 'bg-gradient-to-r from-emerald-400 to-cyan-400',
        amber: 'bg-gradient-to-r from-amber-400 to-orange-400',
        red: 'bg-gradient-to-r from-rose-400 to-pink-500',
        gradient: 'bg-gradient-to-r from-brand-500 via-violet-600 to-cyan-400',
    };

    const trackColors = {
        blue: 'bg-brand-500/20',
        green: 'bg-emerald-400/20',
        amber: 'bg-amber-400/20',
        red: 'bg-rose-400/20',
        gradient: 'bg-white/10',
    };

    return (
        <div className={`w-full ${className}`}>
            {(showLabel || label) && (
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-white/70">
                        {label || 'Score'}
                    </span>
                    {showLabel && (
                        <span className="text-sm font-mono text-brand-400 font-semibold">
                            {percentage.toFixed(1)}%
                        </span>
                    )}
                </div>
            )}
            <div
                className={`${sizeStyles[size]} ${trackColors[color]} rounded-full overflow-hidden relative`}
                role="progressbar"
                aria-valuenow={Math.round(percentage)}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={label || 'Progress'}
            >
                <div
                    className={`${colorStyles[color]} h-full rounded-full transition-all duration-700 ease-out`}
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    );
}

/** Circular progress indicator for similarity scores */
interface CircularProgressProps {
    value: number;
    size?: number;
    strokeWidth?: number;
    color?: 'blue' | 'green' | 'amber' | 'red' | 'gradient';
    showValue?: boolean;
    className?: string;
    animated?: boolean;
}

export function CircularProgress({
    value,
    size = 64,
    strokeWidth = 6,
    color = 'gradient',
    showValue = true,
    className = '',
    animated = true,
}: CircularProgressProps) {
    const percentage = Math.min(Math.max(value, 0), 100);
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;

    const gradientId = `progress-gradient-${Math.random().toString(36).substr(2, 9)}`;

    const getStroke = () => {
        if (color === 'gradient') {
            return `url(#${gradientId})`;
        }
        const colors: Record<string, string> = {
            blue: '#6366f1',
            green: '#10b981',
            amber: '#f59e0b',
            red: '#f43f5e',
        };
        return colors[color];
    };

    const trackColors = {
        blue: 'stroke-brand-500/20',
        green: 'stroke-emerald-400/20',
        amber: 'stroke-amber-400/20',
        red: 'stroke-rose-400/20',
        gradient: 'stroke-white/10',
    };

    return (
        <div className={`relative inline-flex ${className}`} style={{ width: size, height: size }}>
            <svg width={size} height={size} className="transform -rotate-90">
                <defs>
                    <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#6366f1" />
                        <stop offset="50%" stopColor="#8b5cf6" />
                        <stop offset="100%" stopColor="#22d3ee" />
                    </linearGradient>
                </defs>
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    strokeWidth={strokeWidth}
                    className={`${trackColors[color]}`}
                />
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    strokeWidth={strokeWidth}
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    strokeLinecap="round"
                    stroke={getStroke()}
                    className={animated ? 'transition-all duration-700 ease-out' : ''}
                />
            </svg>
            {showValue && (
                <div
                    className="absolute inset-0 flex items-center justify-center"
                    style={{ fontSize: size * 0.22 }}
                >
                    <span className="font-semibold text-white">{percentage.toFixed(0)}%</span>
                </div>
            )}
        </div>
    );
}
