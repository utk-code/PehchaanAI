/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                ocean: {
                    50: '#f0f4f8',
                    100: '#d9e2ec',
                    200: '#bcccdc',
                    300: '#9fb3c8',
                    400: '#829ab1',
                    500: '#627d98',
                    600: '#486581',
                    700: '#334e68',
                    800: '#243b53',
                    900: '#0A1628',
                    950: '#060d18',
                },
                indigo: {
                    450: '#4F46E5',
                    550: '#7C3AED',
                },
                cyan: {
                    450: '#06B6D4',
                },
                emerald: {
                    450: '#10B981',
                },
                amber: {
                    450: '#F59E0B',
                },
                rose: {
                    450: '#F43F5E',
                },
            },
            fontFamily: {
                sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
                display: ['Clash Display', 'Inter', 'sans-serif'],
                mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
            },
            backgroundImage: {
                'gradient-hero': 'linear-gradient(135deg, #0A1628 0%, #1E1B4B 50%, #312E81 100%)',
                'gradient-accent': 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #06B6D4 100%)',
                'gradient-success': 'linear-gradient(135deg, #10B981 0%, #06B6D4 100%)',
                'gradient-warm': 'linear-gradient(135deg, #F59E0B 0%, #F43F5E 100%)',
                'gradient-text': 'linear-gradient(135deg, #06B6D4 0%, #7C3AED 50%, #F43F5E 100%)',
                'gradient-sidebar': 'linear-gradient(180deg, #0A1628 0%, #111827 100%)',
            },
            boxShadow: {
                'glow-indigo': '0 0 20px rgba(79, 70, 229, 0.3), 0 0 40px rgba(79, 70, 229, 0.15)',
                'glow-cyan': '0 0 20px rgba(6, 182, 212, 0.3), 0 0 40px rgba(6, 182, 212, 0.15)',
                'glow-emerald': '0 0 20px rgba(16, 185, 129, 0.3), 0 0 40px rgba(16, 185, 129, 0.15)',
                'glass': '0 4px 24px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
                'glass-elevated': '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.05) inset, 0 1px 0 rgba(255, 255, 255, 0.1) inset',
                'card-lift': '0 12px 40px rgba(0, 0, 0, 0.4)',
            },
            backdropBlur: {
                xs: '2px',
                '2xl': '32px',
                '3xl': '48px',
            },
            animation: {
                'float': 'float 20s ease-in-out infinite',
                'float-slow': 'float 30s ease-in-out infinite',
                'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
                'shimmer': 'shimmer 2s linear infinite',
                'reveal-up': 'reveal-up 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards',
                'reveal-scale': 'reveal-scale 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards',
                'spin-glow': 'spin-glow 1s linear infinite',
                'bounce-in': 'bounce-in 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0) rotate(0deg)' },
                    '50%': { transform: 'translateY(-20px) rotate(2deg)' },
                },
                'pulse-glow': {
                    '0%, 100%': { boxShadow: '0 0 20px rgba(79, 70, 229, 0.3)' },
                    '50%': { boxShadow: '0 0 40px rgba(79, 70, 229, 0.6)' },
                },
                shimmer: {
                    '0%': { backgroundPosition: '-200% 0' },
                    '100%': { backgroundPosition: '200% 0' },
                },
                'reveal-up': {
                    '0%': { opacity: '0', transform: 'translateY(30px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                'reveal-scale': {
                    '0%': { opacity: '0', transform: 'scale(0.95)' },
                    '100%': { opacity: '1', transform: 'scale(1)' },
                },
                'spin-glow': {
                    '0%': { transform: 'rotate(0deg)' },
                    '100%': { transform: 'rotate(360deg)' },
                },
                'bounce-in': {
                    '0%': { opacity: '0', transform: 'scale(0.3)' },
                    '50%': { opacity: '1', transform: 'scale(1.05)' },
                    '70%': { transform: 'scale(0.9)' },
                    '100%': { transform: 'scale(1)' },
                },
            },
            transitionTimingFunction: {
                'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
                'bounce': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
                'elastic': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
                'dramatic': 'cubic-bezier(0.16, 1, 0.3, 1)',
            },
        },
    },
    plugins: [],
}
