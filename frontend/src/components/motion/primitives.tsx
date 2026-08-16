import { motion, AnimatePresence, useReducedMotion, type Variants } from 'framer-motion';
import { ReactNode, useMemo } from 'react';

export const EASE = [0.16, 1, 0.3, 1] as const;
export const EASE_SMOOTH = [0.4, 0, 0.2, 1] as const;

const baseVariants: Variants = {
    hidden: { opacity: 0, y: 24, filter: 'blur(6px)' },
    visible: {
        opacity: 1,
        y: 0,
        filter: 'blur(0px)',
        transition: {
            duration: 0.7,
            ease: EASE,
        },
    },
};

export function Reveal({
    children,
    delay = 0,
    className,
    as = 'div',
    once = true,
}: {
    children: ReactNode;
    delay?: number;
    className?: string;
    as?: 'div' | 'section' | 'span';
    once?: boolean;
}) {
    const reducedMotion = useReducedMotion();
    const Comp = motion[as];

    if (reducedMotion) {
        return <div className={className}>{children}</div>;
    }

    return (
        <Comp
            className={className}
            initial="hidden"
            whileInView="visible"
            viewport={{ once, margin: '-80px' }}
            variants={{
                hidden: baseVariants.hidden,
                visible: {
                    ...baseVariants.visible,
                    transition: {
                        duration: 0.7,
                        ease: EASE,
                        delay,
                    },
                },
            }}
        >
            {children}
        </Comp>
    );
}

export function Stagger({
    children,
    className,
    staggerDelay = 0.08,
}: {
    children: ReactNode;
    className?: string;
    staggerDelay?: number;
}) {
    const reducedMotion = useReducedMotion();

    if (reducedMotion) {
        return <div className={className}>{children}</div>;
    }

    return (
        <motion.div
            className={className}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-80px' }}
            variants={{
                hidden: {},
                visible: {
                    transition: {
                        staggerChildren: staggerDelay,
                    },
                },
            }}
        >
            {children}
        </motion.div>
    );
}

export function StaggerItem({
    children,
    className,
}: {
    children: ReactNode;
    className?: string;
}) {
    const reducedMotion = useReducedMotion();

    if (reducedMotion) {
        return <div className={className}>{children}</div>;
    }

    return (
        <motion.div
            className={className}
            variants={{
                hidden: baseVariants.hidden,
                visible: {
                    ...baseVariants.visible,
                    transition: {
                        duration: 0.7,
                        ease: EASE,
                    },
                },
            }}
        >
            {children}
        </motion.div>
    );
}

export function FadeIn({
    children,
    className,
    delay = 0,
}: {
    children: ReactNode;
    className?: string;
    delay?: number;
}) {
    const reducedMotion = useReducedMotion();

    if (reducedMotion) {
        return <div className={className}>{children}</div>;
    }

    return (
        <motion.div
            className={className}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, ease: EASE_SMOOTH, delay }}
        >
            {children}
        </motion.div>
    );
}

export function ScaleIn({
    children,
    className,
    delay = 0,
}: {
    children: ReactNode;
    className?: string;
    delay?: number;
}) {
    const reducedMotion = useReducedMotion();

    if (reducedMotion) {
        return <div className={className}>{children}</div>;
    }

    return (
        <motion.div
            className={className}
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, ease: EASE, delay }}
        >
            {children}
        </motion.div>
    );
}

export function PageTransition({ children }: { children: ReactNode }) {
    const reducedMotion = useReducedMotion();

    if (reducedMotion) {
        return <div>{children}</div>;
    }

    return (
        <AnimatePresence mode="wait">
            <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                transition={{ duration: 0.35, ease: EASE_SMOOTH }}
            >
                {children}
            </motion.div>
        </AnimatePresence>
    );
}

export function useStaggerCount(count: number) {
    return useMemo(() => Array.from({ length: count }, (_, i) => i), [count]);
}
