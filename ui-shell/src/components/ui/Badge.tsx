import * as React from 'react';
import { cn } from '@/lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'destructive' | 'outline';
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
    ({ className, variant = 'default', ...props }, ref) => {
        const variantClasses = {
            default: 'bg-muted text-muted-foreground',
            primary: 'bg-primary text-primary-foreground',
            secondary: 'bg-secondary text-secondary-foreground',
            success: 'bg-green-500 text-white',
            warning: 'bg-yellow-500 text-white',
            destructive: 'bg-destructive text-destructive-foreground',
            outline: 'border border-input bg-background text-foreground',
        };

        return (
            <div
                ref={ref}
                className={cn(
                    'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors',
                    variantClasses[variant],
                    className
                )}
                {...props}
            />
        );
    }
);

Badge.displayName = 'Badge';

export { Badge };
